#!/usr/bin/env python3
"""Generate and report on the locked (fully pinned) project manifest.

The locked manifest records the project revisions that passed a full nightly
build. It is never hand-edited: this script produces it from a CI candidate
snapshot or a local workspace, rejects anything that is not fully pinned, and
reports which commits a promotion crosses so the Gerrit review has something
concrete to look at.

The same report doubles as nightly triage output: run without --write to answer
"what landed since the last known-good snapshot" when a floating build breaks.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import yaml

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
# Keep the banner above `manifest:` when rewriting, so the "do not hand-edit"
# and usage notes survive every promotion.
BANNER_END = "manifest:"


class LockError(RuntimeError):
    """Lock contents, promotion inputs, or workspace state are unusable."""


@dataclass(frozen=True)
class PinnedProject:
    name: str
    revision: str
    path: str


@dataclass(frozen=True)
class ProjectChange:
    name: str
    kind: str  # added | removed | moved | unchanged
    old_revision: str
    new_revision: str
    commits: tuple[str, ...]
    note: str


def _git(repository: Path, *args: str) -> tuple[int, str]:
    process = subprocess.run(
        ["git", "-C", str(repository), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return process.returncode, process.stdout.strip()


def freeze_workspace(workspace: Path) -> str:
    """Capture `west manifest --freeze` for a workspace that is already updated."""
    process = subprocess.run(
        ["west", "manifest", "--freeze"],
        cwd=str(workspace),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if process.returncode != 0:
        raise LockError(f"west manifest --freeze failed in {workspace}:\n{process.stderr.strip()}")
    return process.stdout


def parse_projects(text: str, source: str) -> dict[str, PinnedProject]:
    """Read project name/revision/path triples out of a manifest document."""
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise LockError(f"{source} is not valid YAML: {exc}") from exc
    if not isinstance(document, dict) or "manifest" not in document:
        raise LockError(f"{source} has no top-level 'manifest' key")

    projects = document["manifest"].get("projects")
    if not isinstance(projects, list) or not projects:
        raise LockError(f"{source} declares no projects")

    parsed: dict[str, PinnedProject] = {}
    for entry in projects:
        if not isinstance(entry, dict) or "name" not in entry:
            raise LockError(f"{source} has a project entry without a name: {entry!r}")
        name = str(entry["name"])
        if name in parsed:
            raise LockError(f"{source} declares project {name!r} twice")
        parsed[name] = PinnedProject(
            name=name,
            revision=str(entry.get("revision", "")),
            path=str(entry.get("path", "")),
        )
    return parsed


def ensure_pinned(projects: dict[str, PinnedProject], source: str) -> None:
    """Reject a candidate whose revisions are not all full 40-hex SHAs.

    A branch name that slips through here would silently turn the locked
    manifest back into a floating one, which is the exact failure this whole
    mechanism exists to prevent.
    """
    unpinned = sorted(
        f"{project.name}={project.revision or '<missing>'}"
        for project in projects.values()
        if not FULL_SHA.match(project.revision)
    )
    if unpinned:
        raise LockError(
            f"{source} is not fully pinned; every revision must be a 40-hex SHA:\n"
            + "\n".join(f"  - {item}" for item in unpinned)
        )


def ensure_same_project_set(
    candidate: dict[str, PinnedProject],
    floating: dict[str, PinnedProject],
) -> None:
    """Guard against promoting a snapshot taken from a different manifest."""
    missing = sorted(set(floating) - set(candidate))
    extra = sorted(set(candidate) - set(floating))
    problems = []
    if missing:
        problems.append(f"missing from candidate: {', '.join(missing)}")
    if extra:
        problems.append(f"absent from floating manifest: {', '.join(extra)}")
    if problems:
        raise LockError("Candidate does not match the floating manifest; " + "; ".join(problems))


def _commits_between(
    repository: Path,
    old_revision: str,
    new_revision: str,
    limit: int,
) -> tuple[tuple[str, ...], str]:
    """List `old..new` subjects, degrading gracefully when objects are absent.

    A force-push upstream can make the previously locked SHA unreachable. That
    is worth reporting rather than crashing, because it also means the old lock
    can no longer be checked out.
    """
    if not (repository / ".git").exists():
        return (), f"repository not present at {repository}"

    for revision in (old_revision, new_revision):
        code, _ = _git(repository, "cat-file", "-e", f"{revision}^{{commit}}")
        if code != 0:
            return (), f"commit {revision[:12]} is not reachable locally"

    code, output = _git(
        repository,
        "log",
        "--no-merges",
        f"--max-count={limit + 1}",
        "--format=%h %s",
        f"{old_revision}..{new_revision}",
    )
    if code != 0:
        return (), f"git log {old_revision[:12]}..{new_revision[:12]} failed"

    lines = [line for line in output.splitlines() if line.strip()]
    if len(lines) > limit:
        return tuple(lines[:limit]), f"truncated, more than {limit} commits"
    return tuple(lines), ""


def diff_projects(
    old: dict[str, PinnedProject],
    new: dict[str, PinnedProject],
    workspace: Path | None,
    limit: int,
) -> list[ProjectChange]:
    changes: list[ProjectChange] = []
    for name in sorted(set(old) | set(new)):
        before = old.get(name)
        after = new.get(name)
        if before is None and after is not None:
            changes.append(ProjectChange(name, "added", "", after.revision, (), ""))
            continue
        if after is None and before is not None:
            changes.append(ProjectChange(name, "removed", before.revision, "", (), ""))
            continue
        assert before is not None and after is not None
        if before.revision == after.revision:
            changes.append(
                ProjectChange(name, "unchanged", before.revision, after.revision, (), "")
            )
            continue

        commits: tuple[str, ...] = ()
        note = "no workspace supplied, commit list unavailable"
        if workspace is not None:
            commits, note = _commits_between(
                workspace / after.path, before.revision, after.revision, limit
            )
        changes.append(
            ProjectChange(name, "moved", before.revision, after.revision, commits, note)
        )
    return changes


def render_report(changes: Sequence[ProjectChange], title: str) -> str:
    moved = [change for change in changes if change.kind == "moved"]
    added = [change for change in changes if change.kind == "added"]
    removed = [change for change in changes if change.kind == "removed"]
    unchanged = [change for change in changes if change.kind == "unchanged"]

    lines = [f"# {title}", ""]
    if not moved and not added and not removed:
        lines += ["Locked manifest already matches the candidate; nothing to promote.", ""]
        return "\n".join(lines)

    lines += [
        f"- Projects moved: **{len(moved)}**",
        f"- Projects added: **{len(added)}**, removed: **{len(removed)}**",
        f"- Projects unchanged: {len(unchanged)}",
        "",
    ]

    for change in moved:
        lines += [
            f"## {change.name}",
            "",
            f"`{change.old_revision[:12]}` -> `{change.new_revision[:12]}`",
            "",
        ]
        if change.commits:
            lines += [f"- {commit}" for commit in change.commits]
        else:
            lines.append(f"- _{change.note or 'no commit details'}_")
        if change.commits and change.note:
            lines.append(f"- _{change.note}_")
        lines.append("")

    for change in added:
        lines += [f"## {change.name} (added)", "", f"pinned at `{change.new_revision[:12]}`", ""]
    for change in removed:
        lines += [f"## {change.name} (removed)", "", f"was `{change.old_revision[:12]}`", ""]

    return "\n".join(lines)


def split_banner(existing: str) -> str:
    """Return the leading comment banner of an existing lock file."""
    head: list[str] = []
    for line in existing.splitlines():
        if line.startswith(BANNER_END):
            break
        head.append(line)
    return "\n".join(head).rstrip() + "\n" if head else ""


def write_lock(lock_path: Path, candidate_text: str, verified_note: str | None) -> None:
    banner = split_banner(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else ""
    if verified_note and banner:
        banner = re.sub(
            r"^# verified:.*(?:\n#\s{2,}.*)*",
            f"# verified: {verified_note}",
            banner,
            count=1,
            flags=re.MULTILINE,
        )
    body = candidate_text[candidate_text.index(BANNER_END) :]
    lock_path.write_text(banner + body, encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate, report on, and write the locked manifest"
    )
    parser.add_argument("--lock", type=Path, required=True, help="Locked manifest to compare/write")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--candidate", type=Path, help="CI candidate snapshot (freeze output)")
    source.add_argument("--workspace", type=Path, help="Updated West workspace to freeze")
    parser.add_argument(
        "--floating",
        type=Path,
        help="Floating manifest to cross-check the project set against",
    )
    parser.add_argument(
        "--repos",
        type=Path,
        help="Workspace root used to resolve commit lists (defaults to --workspace)",
    )
    parser.add_argument("--report", type=Path, help="Write the Markdown report here")
    parser.add_argument("--max-commits", type=int, default=40)
    parser.add_argument(
        "--verified",
        help="Value for the 'verified:' banner line, e.g. a CI run URL",
    )
    parser.add_argument("--write", action="store_true", help="Update the locked manifest in place")
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Exit non-zero when the candidate differs from the lock (CI drift check)",
    )
    args = parser.parse_args(argv)
    if args.max_commits < 1:
        parser.error("--max-commits must be greater than 0")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    # Commit subjects arrive as UTF-8; the Windows console defaults to cp936
    # and would otherwise mangle or refuse them.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        if args.workspace:
            candidate_text = freeze_workspace(args.workspace.expanduser().resolve())
            candidate_source = f"freeze of {args.workspace}"
        else:
            candidate_text = args.candidate.read_text(encoding="utf-8")
            candidate_source = str(args.candidate)

        candidate = parse_projects(candidate_text, candidate_source)
        ensure_pinned(candidate, candidate_source)

        if args.floating:
            floating = parse_projects(
                args.floating.read_text(encoding="utf-8"), str(args.floating)
            )
            ensure_same_project_set(candidate, floating)

        old: dict[str, PinnedProject] = {}
        if args.lock.is_file():
            old = parse_projects(args.lock.read_text(encoding="utf-8"), str(args.lock))
            ensure_pinned(old, str(args.lock))

        repos = args.repos or args.workspace
        changes = diff_projects(
            old,
            candidate,
            repos.expanduser().resolve() if repos else None,
            args.max_commits,
        )
        title = "Locked manifest promotion" if args.write else "Drift against locked manifest"
        report = render_report(changes, title)

        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(report, encoding="utf-8")
        print(report)

        drifted = any(change.kind != "unchanged" for change in changes)
        if args.write:
            if not drifted:
                print(f"Locked manifest is already current: {args.lock}")
                return 0
            write_lock(args.lock, candidate_text, args.verified)
            print(f"Locked manifest written: {args.lock}")
            print("Submit it through Gerrit; never push it straight to Gitee/GitHub.")
            return 0

        if drifted and args.fail_on_drift:
            return 1
        return 0
    except LockError as exc:
        print(f"Lock error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"I/O error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
