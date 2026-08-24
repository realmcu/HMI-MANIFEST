#!/usr/bin/env python3
"""Promote a GitHub-verified lock package through the local Gerrit workflow.

GitHub Actions builds the floating manifest and publishes a promotion package,
but never writes git history. This script downloads and validates that package,
then deliberately splits the local side into two commands:

  prepare  download, validate, create a branch, and update the lock file
  submit   commit the reviewed diff and push it to Gerrit for review

The split leaves an explicit review point (`git diff`) before the outward-facing
Gerrit push. Lock contents are copied byte-for-byte from the CI package; the
script never derives revisions on the developer PC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import yaml

from bump_lock import LockError, ensure_pinned, ensure_same_project_set, parse_projects

DEFAULT_REPOSITORY = "realmcu/HMI-MANIFEST"
DEFAULT_WORKFLOW = "nightly-verification.yml"
ARTIFACT_PREFIX = "dashboard-lock-promotion-"
LOCK_NAME = "rtl8773e-dashboard-gitee.lock.yml"
FLOATING_NAME = "rtl8773e-dashboard-gitee.yml"
METADATA_NAME = "promotion-metadata.json"
REPORT_NAME = "promotion-report.md"
STATE_NAME = "lock-promotion-state.json"
EXPECTED_METADATA_KEYS = {
    "schema_version",
    "repository",
    "workflow_file",
    "run_id",
    "run_attempt",
    "run_url",
    "manifest_commit",
    "source_manifest",
    "source_manifest_sha256",
    "lock_file",
    "lock_sha256",
    "track",
    "build_result",
}
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


class PromotionError(RuntimeError):
    """Promotion input, provenance, or local git state is unsafe."""


@dataclass(frozen=True)
class Artifact:
    name: str
    run_id: int
    expired: bool
    created_at: str
    head_branch: str
    head_sha: str


@dataclass(frozen=True)
class PromotionPackage:
    directory: Path
    lock_path: Path
    report_path: Path
    metadata: dict[str, Any]


def run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )
    if check and process.returncode != 0:
        output = "\n".join(
            part.strip() for part in (process.stdout, process.stderr) if part.strip()
        )
        raise PromotionError(f"Command failed: {' '.join(command)}\n{output}")
    return process


def git(manifest_repo: Path, *args: str, check: bool = True) -> str:
    return run(["git", "-C", str(manifest_repo), *args], check=check).stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise PromotionError(f"Required command is missing: {name}")


def require_clean(manifest_repo: Path) -> None:
    status = git(manifest_repo, "status", "--porcelain")
    if status:
        raise PromotionError(
            "The manifest repository must be clean before prepare.\n"
            f"Current changes:\n{status}"
        )


def git_path(manifest_repo: Path, name: str) -> Path:
    value = git(manifest_repo, "rev-parse", "--path-format=absolute", "--git-path", name)
    return Path(value)


def common_git_dir(manifest_repo: Path) -> Path:
    return Path(
        git(manifest_repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    )


def state_path(manifest_repo: Path) -> Path:
    return common_git_dir(manifest_repo) / STATE_NAME


def load_json(path: Path, description: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionError(f"Unable to read {description} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PromotionError(f"{description} must be a JSON object: {path}")
    return value


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_artifacts(document: dict[str, Any]) -> list[Artifact]:
    raw_artifacts = document.get("artifacts")
    if not isinstance(raw_artifacts, list):
        raise PromotionError("GitHub artifact response has no 'artifacts' array")

    artifacts: list[Artifact] = []
    for entry in raw_artifacts:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        workflow_run = entry.get("workflow_run")
        if not isinstance(name, str) or not name.startswith(ARTIFACT_PREFIX):
            continue
        if not isinstance(workflow_run, dict) or not isinstance(workflow_run.get("id"), int):
            continue
        artifacts.append(
            Artifact(
                name=name,
                run_id=workflow_run["id"],
                expired=bool(entry.get("expired", False)),
                created_at=str(entry.get("created_at", "")),
                head_branch=str(workflow_run.get("head_branch", "")),
                head_sha=str(workflow_run.get("head_sha", "")),
            )
        )
    return artifacts


def query_artifacts(repository: str) -> list[Artifact]:
    artifacts: list[Artifact] = []
    page = 1
    while True:
        process = run(
            [
                "gh",
                "api",
                f"repos/{repository}/actions/artifacts?per_page=100&page={page}",
            ]
        )
        try:
            document = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            raise PromotionError(f"GitHub returned invalid artifact JSON: {exc}") from exc
        if not isinstance(document, dict):
            raise PromotionError("GitHub artifact response must be a JSON object")
        page_artifacts = document.get("artifacts")
        artifacts.extend(parse_artifacts(document))
        if not isinstance(page_artifacts, list) or len(page_artifacts) < 100:
            break
        page += 1
    return artifacts


def select_artifact(artifacts: Sequence[Artifact], run_id: int | None) -> Artifact:
    candidates = [artifact for artifact in artifacts if not artifact.expired]
    if run_id is not None:
        candidates = [artifact for artifact in candidates if artifact.run_id == run_id]
    if not candidates:
        requested = f" for run {run_id}" if run_id is not None else ""
        raise PromotionError(f"No unexpired lock promotion artifact found{requested}")
    candidates = [artifact for artifact in candidates if artifact.head_branch == "master"]
    if not candidates:
        raise PromotionError("No lock promotion artifact from the master branch was found")
    # The API returns newest first, but sort explicitly instead of relying on it.
    return max(candidates, key=lambda artifact: (artifact.created_at, artifact.run_id))


def download_artifact(repository: str, artifact: Artifact, destination: Path) -> None:
    run(
        [
            "gh",
            "run",
            "download",
            str(artifact.run_id),
            "--repo",
            repository,
            "--name",
            artifact.name,
            "--dir",
            str(destination),
        ]
    )


def validate_package(
    directory: Path,
    *,
    repository: str,
    workflow: str,
    expected_run_id: int | None,
    expected_manifest_commit: str | None,
    floating_path: Path,
) -> PromotionPackage:
    lock_path = directory / LOCK_NAME
    report_path = directory / REPORT_NAME
    metadata_path = directory / METADATA_NAME
    packaged_floating = directory / FLOATING_NAME
    missing = [
        str(path.name)
        for path in (lock_path, report_path, metadata_path, packaged_floating)
        if not path.is_file()
    ]
    if missing:
        raise PromotionError(f"Promotion package is incomplete; missing: {', '.join(missing)}")

    metadata = load_json(metadata_path, "promotion metadata")
    unknown = set(metadata) - EXPECTED_METADATA_KEYS
    missing_keys = EXPECTED_METADATA_KEYS - set(metadata)
    if missing_keys or unknown:
        details = []
        if missing_keys:
            details.append(f"missing keys: {', '.join(sorted(missing_keys))}")
        if unknown:
            details.append(f"unknown keys: {', '.join(sorted(unknown))}")
        raise PromotionError("Unexpected promotion metadata schema; " + "; ".join(details))

    checks = {
        "schema_version": 1,
        "repository": repository,
        "workflow_file": workflow,
        "source_manifest": FLOATING_NAME,
        "lock_file": LOCK_NAME,
        "track": "floating",
        "build_result": "success",
    }
    for key, expected in checks.items():
        if metadata.get(key) != expected:
            raise PromotionError(
                f"Promotion metadata {key!r} is {metadata.get(key)!r}, expected {expected!r}"
            )

    run_id = metadata.get("run_id")
    if not isinstance(run_id, int) or run_id <= 0:
        raise PromotionError("Promotion metadata run_id must be a positive integer")
    if expected_run_id is not None and run_id != expected_run_id:
        raise PromotionError(
            f"Promotion package says run {run_id}, but artifact came from run {expected_run_id}"
        )
    if metadata.get("run_url") != f"https://github.com/{repository}/actions/runs/{run_id}":
        raise PromotionError("Promotion metadata run_url does not match repository and run_id")

    manifest_commit = metadata.get("manifest_commit")
    if not isinstance(manifest_commit, str) or not FULL_SHA.match(manifest_commit):
        raise PromotionError("Promotion metadata manifest_commit is not a full commit SHA")
    if expected_manifest_commit and manifest_commit != expected_manifest_commit:
        raise PromotionError(
            "Promotion metadata manifest_commit does not match the selected "
            "GitHub Actions run"
        )

    expected_source_hash = metadata.get("source_manifest_sha256")
    packaged_source_hash = sha256(packaged_floating)
    if not isinstance(expected_source_hash, str) or expected_source_hash != packaged_source_hash:
        raise PromotionError(
            "SHA-256 mismatch for the packaged floating manifest: "
            f"metadata={expected_source_hash!r}, actual={packaged_source_hash}"
        )

    expected_lock_hash = metadata.get("lock_sha256")
    actual_lock_hash = sha256(lock_path)
    if not isinstance(expected_lock_hash, str) or expected_lock_hash != actual_lock_hash:
        raise PromotionError(
            f"SHA-256 mismatch for {lock_path.name}: "
            f"metadata={expected_lock_hash!r}, actual={actual_lock_hash}"
        )

    try:
        lock_projects = parse_projects(lock_path.read_text(encoding="utf-8"), str(lock_path))
        ensure_pinned(lock_projects, str(lock_path))
        packaged_projects = parse_projects(
            packaged_floating.read_text(encoding="utf-8"), str(packaged_floating)
        )
        ensure_same_project_set(lock_projects, packaged_projects)
        current_projects = parse_projects(
            floating_path.read_text(encoding="utf-8"), str(floating_path)
        )
        ensure_same_project_set(lock_projects, current_projects)
    except LockError as exc:
        raise PromotionError(str(exc)) from exc

    ensure_source_compatible(packaged_floating, floating_path)

    return PromotionPackage(directory, lock_path, report_path, metadata)


def verify_manifest_commit(manifest_repo: Path, commit: str) -> None:
    # The package is downloaded from GitHub using gh, then independently bound
    # to a commit reachable from the expected public mirror branch.
    git(manifest_repo, "fetch", "github", "master")
    result = run(
        [
            "git",
            "-C",
            str(manifest_repo),
            "merge-base",
            "--is-ancestor",
            commit,
            "github/master",
        ],
        check=False,
    )
    if result.returncode != 0:
        raise PromotionError(
            f"CI manifest commit {commit} is not reachable from github/master"
        )


def manifest_structure(text: str, source: str) -> list[dict[str, Any]]:
    """Extract compatibility-relevant fields while ignoring branch movement.

    The source manifest can gain an unrelated README/CI commit, and branch tips
    naturally move between nightly and promotion. What must invalidate an old
    package is a structural change: project membership, URL selection, checkout
    path, branch name, imports, groups, or West command extensions.
    """
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise PromotionError(f"Unable to parse {source}: {exc}") from exc
    if not isinstance(document, dict) or not isinstance(document.get("manifest"), dict):
        raise PromotionError(f"{source} has no top-level manifest mapping")
    projects = document["manifest"].get("projects")
    if not isinstance(projects, list):
        raise PromotionError(f"{source} has no project list")

    normalized: list[dict[str, Any]] = []
    for project in projects:
        if not isinstance(project, dict):
            raise PromotionError(f"{source} has an invalid project entry")
        normalized.append(
            {
                key: project.get(key)
                for key in (
                    "name",
                    "url",
                    "remote",
                    "repo-path",
                    "revision",
                    "path",
                    "clone-depth",
                    "west-commands",
                    "import",
                    "groups",
                    "submodules",
                )
                if key in project
            }
        )
    return normalized


def ensure_source_compatible(packaged: Path, current: Path) -> None:
    packaged_structure = manifest_structure(
        packaged.read_text(encoding="utf-8"), str(packaged)
    )
    current_structure = manifest_structure(
        current.read_text(encoding="utf-8"), str(current)
    )
    if packaged_structure != current_structure:
        raise PromotionError(
            "The floating manifest structure changed after this CI package was "
            "produced; run the nightly again and promote its new artifact"
        )


def ensure_expected_diff(manifest_repo: Path, expected_file: str) -> None:
    staged = git(manifest_repo, "diff", "--cached", "--name-only")
    if staged:
        raise PromotionError(f"Unexpected staged changes:\n{staged}")

    status = [
        line
        for line in git(manifest_repo, "status", "--porcelain", "--untracked-files=all").splitlines()
        if line
    ]
    changed = [line[3:] for line in status if len(line) >= 4]
    if changed != [expected_file]:
        shown = ", ".join(changed) if changed else "<none>"
        raise PromotionError(
            f"Expected only {expected_file} to be modified; actual changes: {shown}"
        )
    if status[0].startswith("?? "):
        text = (manifest_repo / expected_file).read_text(encoding="utf-8")
        bad_lines = [
            index
            for index, line in enumerate(text.splitlines(), start=1)
            if line.rstrip() != line
        ]
        if bad_lines:
            raise PromotionError(
                f"New lock file has trailing whitespace on lines: {bad_lines}"
            )
    else:
        check = run(
            ["git", "-C", str(manifest_repo), "diff", "--check"],
            check=False,
        )
        if check.returncode != 0:
            raise PromotionError(f"git diff --check failed:\n{check.stdout}{check.stderr}")


def prepare(args: argparse.Namespace, manifest_repo: Path) -> int:
    require_command("git")
    pending_state = state_path(manifest_repo)
    if pending_state.exists():
        raise PromotionError(
            f"A promotion is already prepared: {pending_state}\n"
            "Submit it or delete the state file after manually abandoning its worktree."
        )

    floating_path = manifest_repo / FLOATING_NAME
    target_lock = manifest_repo / LOCK_NAME
    if not floating_path.is_file() or not target_lock.is_file():
        raise PromotionError("Run this script from the manifest repository checkout")

    temporary: tempfile.TemporaryDirectory[str] | None = None
    promotion_worktree: Path | None = None
    prepared = False
    expected_run_id: int | None = args.run_id
    try:
        if args.package:
            package_dir = args.package.expanduser().resolve()
        else:
            require_command("gh")
            artifact = select_artifact(query_artifacts(args.repository), args.run_id)
            expected_run_id = artifact.run_id
            temporary = tempfile.TemporaryDirectory(prefix="lock-promotion-")
            package_dir = Path(temporary.name)
            print(f"Downloading {artifact.name} from GitHub run {artifact.run_id}...")
            download_artifact(args.repository, artifact, package_dir)

        package = validate_package(
            package_dir,
            repository=args.repository,
            workflow=args.workflow,
            expected_run_id=expected_run_id,
            expected_manifest_commit=(artifact.head_sha if not args.package else None),
            floating_path=floating_path,
        )
        run_id = int(package.metadata["run_id"])
        candidate_hash = str(package.metadata["lock_sha256"])

        if sha256(target_lock) == candidate_hash:
            print(f"Lock already contains GitHub run {run_id}; nothing to promote.")
            return 0

        verify_manifest_commit(
            manifest_repo,
            str(package.metadata["manifest_commit"]),
        )
        git(manifest_repo, "fetch", "gerrit", "master")

        branch = f"promote-dashboard-lock-{run_id}"
        branch_check = run(
            [
                "git",
                "-C",
                str(manifest_repo),
                "show-ref",
                "--verify",
                "--quiet",
                f"refs/heads/{branch}",
            ],
            check=False,
        )
        if branch_check.returncode == 0:
            raise PromotionError(
                f"Local branch {branch} already exists; inspect or delete it before retrying"
            )

        worktree_root = common_git_dir(manifest_repo) / "lock-promotions"
        promotion_worktree = worktree_root / str(run_id)
        if promotion_worktree.exists():
            raise PromotionError(
                f"Promotion worktree already exists: {promotion_worktree}; "
                "inspect or remove it before retrying"
            )
        worktree_root.mkdir(parents=True, exist_ok=True)
        git(
            manifest_repo,
            "worktree",
            "add",
            "-b",
            branch,
            str(promotion_worktree),
            "gerrit/master",
        )

        promotion_floating = promotion_worktree / FLOATING_NAME
        promotion_lock = promotion_worktree / LOCK_NAME
        # Revalidate against the actual Gerrit base checked out in the isolated
        # worktree. The user's current branch and unrelated edits stay untouched.
        package = validate_package(
            package_dir,
            repository=args.repository,
            workflow=args.workflow,
            expected_run_id=run_id,
            expected_manifest_commit=(artifact.head_sha if not args.package else None),
            floating_path=promotion_floating,
        )
        promotion_lock.write_bytes(package.lock_path.read_bytes())
        ensure_expected_diff(promotion_worktree, LOCK_NAME)

        state = {
            "schema_version": 1,
            "phase": "prepared",
            "branch": branch,
            "worktree": str(promotion_worktree),
            "base": git(manifest_repo, "rev-parse", "gerrit/master"),
            "run_id": run_id,
            "run_url": package.metadata["run_url"],
            "manifest_commit": package.metadata["manifest_commit"],
            "lock_sha256": candidate_hash,
        }
        save_state(pending_state, state)
        prepared = True

        # Stop retaining references to temporary package paths before cleanup
        # (important on Windows).
        del package
        print(f"Prepared GitHub run {run_id} on branch {branch}.")
        print(f"Build: {state['run_url']}")
        print(f"Isolated worktree: {promotion_worktree}")
        print("\nReview before submitting:")
        print(f"  git -C {promotion_worktree} diff -- {LOCK_NAME}")
        print(f"  python {Path(__file__).resolve()} submit")
        return 0
    finally:
        if temporary is not None:
            temporary.cleanup()
        if promotion_worktree is not None and not prepared:
            if promotion_worktree.exists():
                run(
                    [
                        "git",
                        "-C",
                        str(manifest_repo),
                        "worktree",
                        "remove",
                        "--force",
                        str(promotion_worktree),
                    ],
                    check=False,
                )
            if "branch" in locals():
                run(
                    ["git", "-C", str(manifest_repo), "branch", "-D", branch],
                    check=False,
                )


def commit_message(state: dict[str, Any]) -> tuple[str, str]:
    subject = "manifest: promote dashboard lock"
    body = (
        "Promote the RTL8773E Dashboard lock to revisions verified by the\n"
        "GitHub nightly full build.\n\n"
        f"GitHub run: {state['run_id']}\n"
        f"Manifest: {state['manifest_commit']}"
    )
    if len(subject) > 50 or any(len(line) > 72 for line in body.splitlines()):
        raise PromotionError("Generated commit message violates Gerrit length limits")
    return subject, body


def validate_state(state: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "phase",
        "branch",
        "worktree",
        "base",
        "run_id",
        "run_url",
        "manifest_commit",
        "lock_sha256",
    }
    expected = required | ({"commit"} if state.get("phase") == "committed" else set())
    if set(state) != expected:
        raise PromotionError("Promotion state has an unexpected schema")
    if state["schema_version"] != 1 or state["phase"] not in {"prepared", "committed"}:
        raise PromotionError("Promotion state has an unsupported version or phase")
    if not isinstance(state["worktree"], str) or not state["worktree"]:
        raise PromotionError("Promotion state has no valid worktree path")
    if state["phase"] == "committed":
        commit = state["commit"]
        if not isinstance(commit, str) or not FULL_SHA.match(commit):
            raise PromotionError("Committed promotion state has no valid commit SHA")


def submit(_args: argparse.Namespace, manifest_repo: Path) -> int:
    require_command("git")
    pending_state = state_path(manifest_repo)
    if not pending_state.is_file():
        raise PromotionError("No prepared promotion found; run 'prepare' first")
    state = load_json(pending_state, "promotion state")
    validate_state(state)

    promotion_worktree = Path(state["worktree"])
    if not promotion_worktree.is_dir():
        raise PromotionError(f"Prepared promotion worktree is missing: {promotion_worktree}")
    branch = git(promotion_worktree, "branch", "--show-current")
    if branch != state["branch"]:
        raise PromotionError(
            f"Prepared branch is {state['branch']}, but worktree branch is "
            f"{branch or 'DETACHED'}"
        )

    target_lock = promotion_worktree / LOCK_NAME
    if sha256(target_lock) != state["lock_sha256"]:
        raise PromotionError(
            "The prepared lock changed after validation; rerun prepare instead of submitting"
        )

    if state["phase"] == "prepared":
        ensure_expected_diff(promotion_worktree, LOCK_NAME)
        hook = common_git_dir(manifest_repo) / "hooks" / "commit-msg"
        if not hook.is_file():
            raise PromotionError(
                f"Gerrit commit-msg hook is missing: {hook}\n"
                "Run setup-gerrit-remotes.ps1 before submitting."
            )

        subject, body = commit_message(state)
        git(promotion_worktree, "add", "--", LOCK_NAME)
        # capture_output remains enabled so commit hooks cannot flood the caller,
        # while any failure is still surfaced verbatim by run().
        git(promotion_worktree, "commit", "-m", subject, "-m", body)
        commit = git(promotion_worktree, "rev-parse", "HEAD")
        message = git(promotion_worktree, "log", "-1", "--format=%B")
        if not re.search(r"^Change-Id: I[0-9a-f]{40}$", message, re.MULTILINE):
            raise PromotionError(
                "Commit was created but has no Gerrit Change-Id; do not push it. "
                "Restore the commit-msg hook and amend through the normal workflow."
            )
        state["phase"] = "committed"
        state["commit"] = commit
        save_state(pending_state, state)
        print(f"Created commit {commit[:12]}.")
    else:
        commit = state["commit"]
        if git(promotion_worktree, "rev-parse", "HEAD") != commit:
            raise PromotionError("HEAD no longer matches the prepared promotion commit")
        if git(promotion_worktree, "status", "--porcelain"):
            raise PromotionError("Worktree changed after the promotion commit was created")

    remote_url = git(manifest_repo, "remote", "get-url", "gerrit")
    if "cn4soc.rtkbf.com" not in remote_url:
        raise PromotionError(f"Refusing to push to unexpected Gerrit remote: {remote_url}")

    print(f"Pushing {state['branch']} to Gerrit for review...")
    # Explicit `submit` is the user's authorization for this outward-facing push.
    run(
        [
            "git",
            "-C",
            str(promotion_worktree),
            "push",
            "gerrit",
            "HEAD:refs/for/master",
        ],
        capture=False,
    )
    pending_state.unlink()
    run(
        [
            "git",
            "-C",
            str(manifest_repo),
            "worktree",
            "remove",
            str(promotion_worktree),
        ]
    )
    print("Gerrit review submitted successfully; promotion worktree removed.")
    return 0


def status(_args: argparse.Namespace, manifest_repo: Path) -> int:
    path = state_path(manifest_repo)
    if not path.is_file():
        print("No lock promotion is currently prepared.")
        return 0
    state = load_json(path, "promotion state")
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a GitHub-verified lock package through Gerrit"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser(
        "prepare", help="download, validate, and stage a lock update for review"
    )
    prepare_parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    prepare_parser.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    prepare_parser.add_argument("--run-id", type=int, help="promote a specific Actions run")
    prepare_parser.add_argument(
        "--package",
        type=Path,
        help="use an already downloaded promotion package instead of gh",
    )

    subparsers.add_parser("submit", help="commit the reviewed lock and push it to Gerrit")
    subparsers.add_parser("status", help="show the pending local promotion state")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    manifest_repo = Path(__file__).resolve().parents[1]
    try:
        if args.command == "prepare":
            return prepare(args, manifest_repo)
        if args.command == "submit":
            return submit(args, manifest_repo)
        return status(args, manifest_repo)
    except PromotionError as exc:
        print(f"Promotion error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Promotion interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
