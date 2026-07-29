#!/usr/bin/env python3
"""在现有本地 workspace 中验证 RTL8773E Dashboard GCC 构建。"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TypedDict


class BuildDurationSummary(TypedDict):
    by_mode: dict[str, float]
    total: float


PROFILES = {
    "quick": ("src_bank0", "lib_bank0"),
    "full": ("src_bank0", "src_bank1", "lib_bank0", "lib_bank1"),
}
EXPECTED_BANK = {
    "src_bank0": "bank0",
    "src_bank1": "bank1",
    "lib_bank0": "bank0",
    "lib_bank1": "bank1",
}
REQUIRED_TOOLS = ("git", "west", "cmake", "ninja", "arm-none-eabi-gcc")


class VerificationError(RuntimeError):
    """验证配置、环境或安全条件不满足。"""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class WorkspaceLayout:
    name: str
    root: Path
    dashboard_root: Path
    sdk_root: Path


@dataclass(frozen=True)
class RepositoryStatus:
    name: str
    path: str
    remote: str
    branch: str
    commit: str
    dirty: bool


@dataclass(frozen=True)
class ArtifactResult:
    ok: bool
    output_dir: Path
    elf: Path | None
    mp_bin: Path | None
    message: str


@dataclass(frozen=True)
class StepResult:
    status: str
    duration_seconds: float
    log: str
    message: str


def run_command(
    command: Sequence[str],
    cwd: Path | None = None,
    stream: bool = False,
) -> CommandResult:
    """执行命令并捕获输出；stream=True 时同步输出到终端。"""
    process = subprocess.Popen(
        list(command),
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines: list[str] = []
    if process.stdout is None:
        process.kill()
        raise VerificationError(f"无法捕获命令输出：{' '.join(command)}")
    for line in process.stdout:
        lines.append(line)
        if stream:
            print(line, end="")
    returncode = process.wait()
    return CommandResult(returncode, "".join(lines), "")


def discover_workspace(root: Path, name: str = "workspace") -> WorkspaceLayout:
    root = root.expanduser().resolve()
    if not (root / ".west").is_dir():
        raise VerificationError(f"不是 West workspace（缺少 .west）：{root}")

    markers = list(root.glob("**/board/evb/hmi_dashboard/west_commands_extention/west-commands.yml"))
    if len(markers) != 1:
        raise VerificationError(
            f"无法唯一定位 Dashboard project：{root}（找到 {len(markers)} 个）"
        )

    dashboard_root = markers[0].parent.parent
    sdk_root = dashboard_root.parents[2]
    return WorkspaceLayout(name, root, dashboard_root, sdk_root)


def _git_value(path: Path, *args: str) -> str:
    result = run_command(["git", "-C", str(path), *args])
    return result.stdout.strip() if result.returncode == 0 else ""


def inspect_repository(
    path: Path,
    name: str,
    nested_projects: Sequence[Path] = (),
) -> RepositoryStatus:
    """读取仓库状态，并忽略由 West 管理的嵌套 project 根目录。

    Dashboard 仓库中的 Designer UI 是独立 West project。Git 会把这个嵌套仓库
    显示为父仓库的 untracked 目录；它应由自己的 repository status 单独检查，
    不能让干净的 West workspace 被误判为 dirty。
    """
    raw_status = _git_value(path, "status", "--porcelain")
    ignored = set()
    resolved_path = path.resolve()
    for nested in nested_projects:
        try:
            relative = nested.resolve().relative_to(resolved_path).as_posix().rstrip("/")
        except ValueError:
            continue
        if relative:
            ignored.add(relative)

    status_lines = []
    for line in raw_status.splitlines():
        candidate = line[3:].strip().rstrip("/") if len(line) >= 4 else ""
        if line.startswith("?? ") and candidate in ignored:
            continue
        status_lines.append(line)

    return RepositoryStatus(
        name=name,
        path=str(resolved_path),
        remote=_git_value(path, "remote", "get-url", "origin"),
        branch=_git_value(path, "branch", "--show-current") or "DETACHED",
        commit=_git_value(path, "rev-parse", "HEAD"),
        dirty=bool(status_lines),
    )


def list_west_projects(layout: WorkspaceLayout) -> list[RepositoryStatus]:
    separator = "|WEST-PATH|"
    result = run_command(
        ["west", "list", "-f", f"{{name}}{separator}{{abspath}}"], cwd=layout.root
    )
    if result.returncode != 0:
        raise VerificationError(f"west list 失败：\n{result.stdout}")

    project_entries: list[tuple[str, Path]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        try:
            name, path_text = line.split(separator, 1)
        except ValueError as exc:
            raise VerificationError(f"无法解析 west list 输出：{line}") from exc
        project_entries.append((name, Path(path_text)))

    project_paths = [path for _name, path in project_entries]
    return [
        inspect_repository(
            path,
            name,
            nested_projects=[candidate for candidate in project_paths if candidate != path],
        )
        for name, path in project_entries
    ]


def ensure_clean(repositories: Iterable[RepositoryStatus], allow_dirty: bool) -> None:
    dirty = [repository for repository in repositories if repository.dirty]
    if dirty and not allow_dirty:
        details = "\n".join(f"  - {item.name}: {item.path}" for item in dirty)
        raise VerificationError(
            "检测到未提交修改，未开始构建。请先处理工作树，或显式传入 "
            f"--allow-dirty：\n{details}"
        )


def check_tools(include_guilib: bool) -> dict[str, str]:
    tools = list(REQUIRED_TOOLS)
    if include_guilib:
        if os.name != "nt":
            raise VerificationError("west guilib 仅支持 Windows 原生环境")
        tools.append("armclang")

    versions: dict[str, str] = {"platform": platform.platform()}
    missing: list[str] = []
    for tool in tools:
        executable = shutil.which(tool)
        if not executable:
            missing.append(tool)
            continue
        result = run_command([executable, "--version"])
        first_line = (result.stdout.strip().splitlines() or [executable])[0]
        versions[tool] = first_line

    if missing:
        raise VerificationError(f"缺少必需工具：{', '.join(missing)}")
    return versions


def build_command(mode: str, jobs: int) -> list[str]:
    return ["west", "build", "-m", mode, "-c", "-j", str(jobs)]


def inspect_artifacts(sdk_root: Path, mode: str) -> ArtifactResult:
    bank = EXPECTED_BANK[mode]
    output_dir = (
        sdk_root
        / "board"
        / "evb"
        / "hmi_dashboard"
        / "gcc"
        / "bin"
        / f"RTL8773E.hmi_dashboard_{mode}"
    )
    elf = output_dir / f"dashboard_{bank}.elf"
    mp_candidates = sorted(output_dir.glob(f"dashboard_{bank}_MP*.bin"))
    mp_bin = mp_candidates[-1] if mp_candidates else None

    if not elf.is_file() or elf.stat().st_size == 0:
        return ArtifactResult(False, output_dir, None, mp_bin, f"ELF 不存在或为空：{elf}")
    if mp_bin is None or mp_bin.stat().st_size == 0:
        return ArtifactResult(False, output_dir, elf, None, f"MP bin 不存在或为空：{output_dir}")
    return ArtifactResult(True, output_dir, elf, mp_bin, "关键产物检查通过")


def _write_log(path: Path, command: Sequence[str], result: CommandResult) -> None:
    content = f"$ {' '.join(command)}\n\n{result.stdout}"
    if result.stderr:
        content += f"\n[stderr]\n{result.stderr}"
    path.write_text(content, encoding="utf-8")


def run_step(
    command: Sequence[str],
    cwd: Path,
    log_path: Path,
    stream: bool = True,
) -> StepResult:
    started = time.perf_counter()
    result = run_command(command, cwd=cwd, stream=stream)
    duration = time.perf_counter() - started
    _write_log(log_path, command, result)
    status = "PASS" if result.returncode == 0 else "FAIL"
    return StepResult(status, duration, str(log_path), f"exit code {result.returncode}")


def summarize_build_durations(
    builds: Mapping[str, Mapping[str, object]],
) -> BuildDurationSummary:
    """汇总各构建模式的耗时，单位为秒。"""
    by_mode: dict[str, float] = {}
    for mode, result in builds.items():
        duration = result.get("duration_seconds")
        if not isinstance(duration, (int, float)) or not math.isfinite(duration):
            raise VerificationError(f"{mode} 缺少有效的编译耗时")
        if duration < 0:
            raise VerificationError(f"{mode} 的编译耗时不能为负数")
        by_mode[mode] = float(duration)
    return {"by_mode": by_mode, "total": sum(by_mode.values(), 0.0)}


def format_duration(seconds: float) -> str:
    """将非负秒数格式化为秒或“分钟 + 秒”。"""
    if not math.isfinite(seconds) or seconds < 0:
        raise VerificationError("耗时必须是非负有限数值")
    rounded_seconds = round(seconds, 1)
    minutes, remaining_seconds = divmod(rounded_seconds, 60)
    if minutes >= 1:
        return f"{int(minutes)}m {remaining_seconds:.1f}s"
    return f"{remaining_seconds:.1f}s"


def run_builds(
    layout: WorkspaceLayout,
    modes: Sequence[str],
    jobs: int,
    report_dir: Path,
) -> dict[str, dict[str, object]]:
    results: dict[str, dict[str, object]] = {}
    for mode in modes:
        print(f"\n[{layout.name}] 构建 {mode}")
        step = run_step(
            build_command(mode, jobs),
            layout.root,
            report_dir / f"{mode}.log",
        )
        artifact = inspect_artifacts(layout.sdk_root, mode) if step.status == "PASS" else None
        status = "PASS" if step.status == "PASS" and artifact and artifact.ok else "FAIL"
        results[mode] = {
            **asdict(step),
            "status": status,
            "artifact": asdict(artifact) if artifact else None,
        }
        print(
            f"[{layout.name}] {mode}: {status} "
            f"({format_duration(step.duration_seconds)})"
        )
    return results


def run_guilib(layout: WorkspaceLayout, report_dir: Path) -> StepResult:
    return run_step(["west", "guilib"], layout.root, report_dir / "guilib.log")


def run_userdata(layout: WorkspaceLayout, report_dir: Path, required: bool) -> StepResult:
    romfs = (
        layout.dashboard_root
        / "src"
        / "application"
        / "designer"
        / "build"
        / "app_romfs.bin"
    )
    if not romfs.is_file():
        status = "FAIL" if required else "SKIP"
        return StepResult(status, 0.0, "", f"ROMFS 不存在：{romfs}")
    return run_step(
        ["west", "userdata", "--package-only"],
        layout.root,
        report_dir / "userdata.log",
    )


def _json_default(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"无法序列化：{type(value)!r}")


def write_json_report(report_dir: Path, summary: dict[str, object]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )


def write_markdown_report(report_dir: Path, summary: dict[str, object]) -> None:
    lines = ["# Dashboard 本地构建验证结果", ""]
    lines.append(f"- 总体结果：**{summary['overall']}**")
    lines.append(f"- Profile：`{summary['profile']}`")
    lines.append(f"- 生成时间：`{summary['generated_at']}`")
    total_duration = summary.get("total_build_duration_seconds")
    if isinstance(total_duration, (int, float)):
        lines.append(f"- 总编译耗时：`{format_duration(total_duration)}`")
    lines.extend(
        ["", "| Workspace | Mode | Result | Duration |", "|---|---|---|---|"]
    )
    for source, source_result in summary["sources"].items():
        for mode, result in source_result["builds"].items():
            duration = format_duration(result["duration_seconds"])
            lines.append(f"| {source} | {mode} | {result['status']} | {duration} |")
        source_duration = source_result.get("build_duration_seconds", {}).get("total")
        if isinstance(source_duration, (int, float)):
            duration = format_duration(source_duration)
            lines.append(f"| {source} | **Total** | — | **{duration}** |")
    (report_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="在已有本地 Gerrit/Gitee workspace 中验证 Dashboard GCC 构建"
    )
    parser.add_argument("--gerrit", type=Path, help="现有 Gerrit West workspace 根目录")
    parser.add_argument("--gitee", type=Path, help="现有 Gitee West workspace 根目录")
    parser.add_argument("--profile", choices=PROFILES, default="full")
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--guilib", action="store_true")
    parser.add_argument("--userdata", action="store_true")
    parser.add_argument("--userdata-required", action="store_true")
    args = parser.parse_args(argv)
    if not args.gerrit and not args.gitee:
        parser.error("至少指定 --gerrit 或 --gitee")
    if args.jobs < 1:
        parser.error("--jobs 必须大于 0")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        versions = check_tools(args.guilib)
        layouts = []
        if args.gerrit:
            layouts.append(discover_workspace(args.gerrit, "gerrit"))
        if args.gitee:
            layouts.append(discover_workspace(args.gitee, "gitee"))

        now = datetime.now().astimezone()
        generated_at = now.isoformat(timespec="seconds")
        run_id = now.strftime("%Y%m%d-%H%M%S")
        report_root = args.report_dir.expanduser().resolve() / run_id
        sources: dict[str, dict[str, Any]] = {}
        summary: dict[str, object] = {
            "overall": "PASS",
            "profile": args.profile,
            "generated_at": generated_at,
            "tool_versions": versions,
            "sources": sources,
        }

        for layout in layouts:
            print(f"\n验证本地 workspace：{layout.name} -> {layout.root}")
            source_dir = report_root / layout.name
            source_dir.mkdir(parents=True, exist_ok=True)
            repositories = list_west_projects(layout)
            ensure_clean(repositories, args.allow_dirty)
            (source_dir / "revisions.json").write_text(
                json.dumps([asdict(item) for item in repositories], ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            source_result: dict[str, Any] = {
                "workspace": asdict(layout),
                "repositories": [asdict(item) for item in repositories],
                "builds": {},
            }
            if args.guilib:
                source_result["guilib"] = asdict(run_guilib(layout, source_dir))
            source_result["builds"] = run_builds(
                layout, PROFILES[args.profile], args.jobs, source_dir
            )
            source_result["build_duration_seconds"] = summarize_build_durations(
                source_result["builds"]
            )
            if args.userdata or args.userdata_required:
                source_result["userdata"] = asdict(
                    run_userdata(layout, source_dir, args.userdata_required)
                )
            sources[layout.name] = source_result

        total_build_duration = sum(
            (
                source["build_duration_seconds"]["total"]
                for source in sources.values()
            ),
            0.0,
        )
        summary["total_build_duration_seconds"] = total_build_duration
        failed = any(
            result["status"] != "PASS"
            for source in sources.values()
            for result in source["builds"].values()
        )
        optional_failed = any(
            source.get("guilib", {}).get("status") == "FAIL"
            or source.get("userdata", {}).get("status") == "FAIL"
            for source in sources.values()
        )
        if failed or optional_failed:
            summary["overall"] = "FAIL"

        write_json_report(report_root, summary)
        write_markdown_report(report_root, summary)
        print(f"\n总体结果：{summary['overall']}")
        print(f"总编译耗时：{format_duration(total_build_duration)}")
        print(f"报告目录：{report_root}")
        return 0 if summary["overall"] == "PASS" else 1
    except VerificationError as exc:
        print(f"配置或环境错误：{exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\n用户中止验证", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
