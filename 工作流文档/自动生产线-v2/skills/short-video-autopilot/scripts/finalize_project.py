#!/usr/bin/env python3
"""Audit the four final artifacts without moving or cleaning project files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED = {
    "final": "final.mp4",
    "voice": "voice.wav",
    "copy": "copy.md",
    "review": "review.md",
}


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def load_plan(workspace: Path, project: Path) -> tuple[dict, dict[str, Path]]:
    root = workspace.resolve()
    running = root / "视频工作区" / "自动生产线-v2" / "运行中"
    project = project.resolve()
    if not is_within(project, running) or project.parent != running:
        raise ValueError("只允许归档V2运行中目录的直接子项目")
    state_file = project / "pipeline-state.json"
    with state_file.open(encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("stage") != "cleanup_pending":
        raise ValueError(f"项目必须处于 cleanup_pending，当前为：{state.get('stage')}")
    artifacts: dict[str, Path] = {}
    for key in REQUIRED:
        raw = state.get("artifacts", {}).get(key)
        if not raw:
            raise ValueError(f"缺少登记产物：{key}")
        source = Path(raw).resolve()
        if not is_within(source, root):
            raise ValueError(f"产物必须位于当前视频制作工作区内：{source}")
        if not source.is_file() or source.stat().st_size == 0:
            raise ValueError(f"产物不存在或为空：{source}")
        artifacts[key] = source
    return state, artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="V2四项正式成果核验（不整理文件）")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    try:
        workspace = Path(args.workspace)
        project = Path(args.project).resolve()
        _, artifacts = load_plan(workspace, project)
        plan = {
            "mode": "audit_only",
            "project": str(project),
            "files": {REQUIRED[key]: str(source) for key, source in artifacts.items()},
            "file_management": "user_managed",
        }
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if args.commit:
            raise ValueError("用户自行整理项目文件；自动归档、移动和清理已禁用")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
