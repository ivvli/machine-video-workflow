#!/usr/bin/env python3
"""Deterministic state manager for the staged short-video V2 workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


STAGES = {
    "initialized",
    "preflighting",
    "analyzing",
    "copy_review",
    "awaiting_copy_approval",
    "voice_generating",
    "awaiting_voice_approval",
    "script_generating",
    "awaiting_script_approval",
    "editing_framefield",
    "validating",
    "awaiting_upload_approval",
    "exporting",
    "awaiting_cover_choice",
    "publishing_prep",
    "uploading",
    "awaiting_manual_publish",
    "published_waiting_72h",
    "reviewing_72h",
    "cleanup_pending",
    "completed",
    "blocked",
}

TRANSITIONS = {
    "initialized": {"preflighting"},
    "preflighting": {"analyzing"},
    "analyzing": {"copy_review"},
    "copy_review": {"awaiting_copy_approval"},
    "awaiting_copy_approval": {"copy_review", "voice_generating"},
    "voice_generating": {"awaiting_voice_approval"},
    "awaiting_voice_approval": {"voice_generating", "script_generating"},
    "script_generating": {"awaiting_script_approval"},
    "awaiting_script_approval": {"script_generating", "editing_framefield"},
    "editing_framefield": {"validating"},
    "validating": {"editing_framefield", "awaiting_upload_approval"},
    "awaiting_upload_approval": {"editing_framefield"},
    "exporting": {"awaiting_cover_choice"},
    "awaiting_cover_choice": set(),
    "publishing_prep": {"uploading"},
    "uploading": {"awaiting_manual_publish"},
    "awaiting_manual_publish": {"published_waiting_72h"},
    "published_waiting_72h": {"reviewing_72h"},
    "reviewing_72h": {"cleanup_pending"},
    "cleanup_pending": {"completed"},
    "completed": set(),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def state_path(project: Path) -> Path:
    return project.resolve() / "pipeline-state.json"


def load_state(project: Path) -> tuple[Path, dict]:
    path = state_path(project)
    if not path.is_file():
        raise ValueError(f"找不到项目状态文件：{path}")
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("stage") not in STAGES:
        raise ValueError(f"未知项目状态：{data.get('stage')}")
    confirmations = data.setdefault("confirmations", {})
    for kind in ("copy", "voice", "edit_script", "upload", "cover", "manual_publish"):
        confirmations.setdefault(kind, "pending")
    return path, data


def require_framefield_report(data: dict, project_dir: Path, artifact_name: str, marker: str) -> None:
    report = Path(data.get("artifacts", {}).get(artifact_name, ""))
    if not report.is_file() or report.stat().st_size == 0:
        raise ValueError(f"缺少帧场就绪报告：{artifact_name}")
    content = report.read_text(encoding="utf-8")
    if marker not in content:
        raise ValueError(f"帧场就绪报告未通过：{artifact_name}")
    match = re.search(r"^- 工程修订：(\d+)\s*$", content, re.MULTILINE)
    if not match:
        raise ValueError(f"帧场就绪报告缺少工程修订号：{artifact_name}")
    project_file = project_dir / "framefield" / "project.json"
    if not project_file.is_file():
        raise ValueError("帧场工程文件不存在")
    with project_file.open(encoding="utf-8") as handle:
        revision = int(json.load(handle).get("revision", 0))
    if int(match.group(1)) != revision:
        raise ValueError("帧场时间线在就绪检查后又发生变化，请重新预热并检查")


def save_event(path: Path, data: dict, event: str, detail: str = "") -> None:
    timestamp = now_iso()
    data["updated_at"] = timestamp
    data.setdefault("history", []).append(
        {"at": timestamp, "event": event, "stage": data["stage"], "detail": detail}
    )
    atomic_write_json(path, data)


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", value).strip(" ._")
    return cleaned[:60] or "未命名项目"


def workspace_paths(workspace: Path) -> dict[str, Path]:
    root = workspace.resolve()
    return {
        "root": root,
        "pending": root / "原始素材" / "待处理",
        "running": root / "视频工作区" / "自动生产线-v2" / "运行中",
        "completed": root / "视频工作区" / "自动生产线-v2" / "已完成",
    }


def pending_candidates(pending: Path) -> list[Path]:
    pending.mkdir(parents=True, exist_ok=True)
    candidates = [item.resolve() for item in pending.iterdir() if item.is_dir() and not item.name.startswith(".")]
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)


def resolve_source(pending: Path, requested: str | None) -> Path:
    candidates = pending_candidates(pending)
    if requested:
        source = Path(requested).expanduser()
        if not source.is_absolute():
            source = pending / source
        source = source.resolve()
        if source.parent != pending.resolve() or not source.is_dir():
            raise ValueError("素材目录必须是 原始素材/待处理/ 下的直接子目录")
        return source
    if not candidates:
        raise ValueError(f"没有待处理素材，请先放入：{pending}/<产品或主题>/")
    if len(candidates) > 1:
        names = "、".join(item.name for item in candidates)
        raise ValueError(f"发现多个待处理项目，请指定其中一个：{names}")
    return candidates[0]


def next_project_id(running: Path, completed: Path) -> str:
    day = datetime.now().astimezone().strftime("%Y%m%d")
    pattern = re.compile(rf"^P{day}-(\d{{2}})_")
    numbers: list[int] = []
    for parent in (running, completed):
        parent.mkdir(parents=True, exist_ok=True)
        for item in parent.iterdir():
            match = pattern.match(item.name)
            if match:
                numbers.append(int(match.group(1)))
    return f"P{day}-{max(numbers, default=0) + 1:02d}"


def command_init(args: argparse.Namespace) -> None:
    paths = workspace_paths(Path(args.workspace))
    source = resolve_source(paths["pending"], args.source)
    project_id = next_project_id(paths["running"], paths["completed"])
    project_name = safe_name(args.name or source.name)
    project = paths["running"] / f"{project_id}_{project_name}"
    if project.exists():
        raise ValueError(f"项目目录已经存在：{project}")
    project.mkdir(parents=True)
    created = now_iso()
    data = {
        "schema_version": 1,
        "workflow_version": "shadow-v2.3",
        "project_id": project_id,
        "project_name": project_name,
        "workspace_root": str(paths["root"]),
        "source_dir": str(source),
        "stage": "initialized",
        "blocked_from": None,
        "blocked_reason": None,
        "confirmations": {
            "copy": "pending",
            "voice": "pending",
            "edit_script": "pending",
            "upload": "pending",
            "cover": "pending",
            "manual_publish": "pending",
        },
        "revision_rounds": 0,
        "artifacts": {},
        "publication": {"platform": None, "work_id": None, "url": None, "published_at": None},
        "created_at": created,
        "updated_at": created,
        "history": [{"at": created, "event": "initialized", "stage": "initialized", "detail": str(source)}],
    }
    atomic_write_json(project / "pipeline-state.json", data)
    print(json.dumps({"project_dir": str(project), "state": data}, ensure_ascii=False, indent=2))


def assert_transition(current: str, target: str) -> None:
    if target not in STAGES:
        raise ValueError(f"未知目标状态：{target}")
    if current == "blocked":
        raise ValueError("项目已阻塞，请先使用 resume")
    if target == "blocked":
        raise ValueError("请使用 block 命令进入阻塞状态")
    if target not in TRANSITIONS.get(current, set()):
        raise ValueError(f"不允许的状态变化：{current} -> {target}")


def command_transition(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    current = data["stage"]
    assert_transition(current, args.to)
    if current == "preflighting" and args.to == "analyzing":
        preflight = Path(data.get("artifacts", {}).get("preflight", ""))
        if not preflight.is_file() or preflight.stat().st_size == 0:
            raise ValueError("环境预检产物preflight.md不存在或为空")
    if current == "analyzing" and args.to == "copy_review":
        evidence = Path(data.get("artifacts", {}).get("evidence_matrix", ""))
        if not evidence.is_file() or evidence.stat().st_size == 0:
            raise ValueError("文案—证据镜头检查表不存在或为空，不能进入文案审稿")
        content = evidence.read_text(encoding="utf-8")
        if "证据门槛：通过" not in content:
            raise ValueError("文案—证据镜头检查未通过；请补拍或修改文案")
    if current == "script_generating" and args.to == "awaiting_script_approval":
        edit_script = Path(data.get("artifacts", {}).get("edit_script", ""))
        if not edit_script.is_file() or edit_script.stat().st_size == 0:
            raise ValueError("剪辑脚本产物不存在或为空，不能请求确认")
        data["confirmations"]["edit_script"] = "pending"
    if current == "editing_framefield" and args.to == "validating":
        require_framefield_report(data, path.parent, "framefield_edit_ready", "帧场剪辑就绪：通过")
    if current == "validating" and args.to == "editing_framefield":
        data["revision_rounds"] = int(data.get("revision_rounds", 0)) + 1
        if data["revision_rounds"] > 3:
            raise ValueError("自动整改已经达到三轮，请进入阻塞状态")
        data.get("artifacts", {}).pop("framefield_edit_ready", None)
        data.get("artifacts", {}).pop("framefield_preview_ready", None)
        data.get("artifacts", {}).pop("preview", None)
    if current == "validating" and args.to == "awaiting_upload_approval":
        preview = Path(data.get("artifacts", {}).get("preview", ""))
        if not preview.is_file() or preview.stat().st_size == 0:
            raise ValueError("本地检查稿不存在或为空，不能请求上传确认")
        require_framefield_report(data, path.parent, "framefield_preview_ready", "帧场预览就绪：通过")
        data["confirmations"]["upload"] = "pending"
    if current == "awaiting_upload_approval" and args.to == "editing_framefield":
        data["confirmations"]["upload"] = "pending"
        data["confirmations"]["cover"] = "pending"
        data.get("artifacts", {}).pop("framefield_edit_ready", None)
        data.get("artifacts", {}).pop("framefield_preview_ready", None)
        data.get("artifacts", {}).pop("preview", None)
    if current == "exporting" and args.to == "awaiting_cover_choice":
        final = Path(data.get("artifacts", {}).get("final", ""))
        if not final.is_file() or final.stat().st_size == 0:
            raise ValueError("4K成片不存在或为空，不能请求封面方案确认")
        data["confirmations"]["cover"] = "pending"
    if current == "publishing_prep" and args.to == "uploading":
        if data["confirmations"].get("cover") not in {"scrapbook", "user_provided"}:
            raise ValueError("尚未确认封面来源，不能上传")
        cover = Path(data.get("artifacts", {}).get("cover", ""))
        if not cover.is_file() or cover.stat().st_size == 0:
            raise ValueError("封面文件不存在或为空，不能上传")
    if current == "cleanup_pending" and args.to == "completed":
        for key in ("final", "voice", "copy", "review"):
            artifact = Path(data.get("artifacts", {}).get(key, ""))
            if not artifact.is_file() or artifact.stat().st_size == 0:
                raise ValueError(f"缺少非空正式成果：{key}")
    data["stage"] = args.to
    save_event(path, data, "transition", f"{current} -> {args.to}; {args.note or ''}".strip())
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_approve(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    expected = {
        "copy": "awaiting_copy_approval",
        "voice": "awaiting_voice_approval",
        "edit_script": "awaiting_script_approval",
        "upload": "awaiting_upload_approval",
    }
    targets = {
        "copy": "voice_generating",
        "voice": "script_generating",
        "edit_script": "editing_framefield",
        "upload": "exporting",
    }
    if data["stage"] != expected[args.kind]:
        raise ValueError(f"当前状态不能确认{args.kind}：{data['stage']}")
    if args.kind == "edit_script":
        edit_script = Path(data.get("artifacts", {}).get("edit_script", ""))
        if not edit_script.is_file() or edit_script.stat().st_size == 0:
            raise ValueError("剪辑脚本不存在或为空，不能确认")
        data.get("artifacts", {}).pop("framefield_edit_ready", None)
        data.get("artifacts", {}).pop("framefield_preview_ready", None)
    data["confirmations"][args.kind] = "approved"
    current = data["stage"]
    data["stage"] = targets[args.kind]
    save_event(path, data, f"approved_{args.kind}", f"{current} -> {data['stage']}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_reject(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    expected = {
        "copy": "awaiting_copy_approval",
        "voice": "awaiting_voice_approval",
        "edit_script": "awaiting_script_approval",
    }
    targets = {
        "copy": "copy_review",
        "voice": "voice_generating",
        "edit_script": "script_generating",
    }
    if data["stage"] != expected[args.kind]:
        raise ValueError(f"当前状态不能退回{args.kind}：{data['stage']}")
    data["confirmations"][args.kind] = "rejected"
    data["stage"] = targets[args.kind]
    save_event(path, data, f"rejected_{args.kind}", args.reason)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_cover_choice(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    if data["stage"] != "awaiting_cover_choice":
        raise ValueError(f"当前状态不能确认封面方案：{data['stage']}")
    data["confirmations"]["cover"] = args.choice
    data["stage"] = "publishing_prep"
    save_event(path, data, "cover_choice", args.choice)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_artifact(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    artifact = Path(args.path).expanduser().resolve()
    data.setdefault("artifacts", {})[args.name] = str(artifact)
    save_event(path, data, "artifact", f"{args.name}={artifact}")
    print(json.dumps(data["artifacts"], ensure_ascii=False, indent=2))


def command_block(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    if data["stage"] in {"blocked", "completed"}:
        raise ValueError(f"当前状态不能阻塞：{data['stage']}")
    data["blocked_from"] = data["stage"]
    data["blocked_reason"] = args.reason
    data["stage"] = "blocked"
    save_event(path, data, "blocked", args.reason)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_resume(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    if data["stage"] != "blocked" or not data.get("blocked_from"):
        raise ValueError("项目当前没有可恢复的阻塞状态")
    target = data["blocked_from"]
    data["stage"] = target
    data["blocked_from"] = None
    data["blocked_reason"] = None
    save_event(path, data, "resumed", target)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_published(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    if data["stage"] != "awaiting_manual_publish":
        raise ValueError(f"当前状态不能登记发布：{data['stage']}")
    published_at = args.published_at or now_iso()
    parse_time(published_at)
    data["publication"] = {
        "platform": args.platform,
        "work_id": args.work_id,
        "url": args.url,
        "published_at": published_at,
    }
    data["confirmations"]["manual_publish"] = "approved"
    data["stage"] = "published_waiting_72h"
    save_event(path, data, "published", f"{args.platform}:{args.work_id}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_start_review(args: argparse.Namespace) -> None:
    path, data = load_state(Path(args.project))
    if data["stage"] != "published_waiting_72h":
        raise ValueError(f"当前状态不能开始72小时复盘：{data['stage']}")
    published_at = data.get("publication", {}).get("published_at")
    if not published_at:
        raise ValueError("缺少准确发布时间")
    elapsed = datetime.now(timezone.utc) - parse_time(published_at).astimezone(timezone.utc)
    if elapsed.total_seconds() < 72 * 3600 and not args.force_for_test:
        remaining = 72 - elapsed.total_seconds() / 3600
        raise ValueError(f"发布未满72小时，还需约{remaining:.1f}小时")
    data["stage"] = "reviewing_72h"
    save_event(path, data, "review_started", f"elapsed_hours={elapsed.total_seconds()/3600:.2f}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_status(args: argparse.Namespace) -> None:
    _, data = load_state(Path(args.project))
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="短视频自动生产线V2状态管理")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--workspace", required=True)
    init.add_argument("--source")
    init.add_argument("--name")
    init.set_defaults(func=command_init)

    status = sub.add_parser("status")
    status.add_argument("--project", required=True)
    status.set_defaults(func=command_status)

    transition = sub.add_parser("transition")
    transition.add_argument("--project", required=True)
    transition.add_argument("--to", required=True)
    transition.add_argument("--note")
    transition.set_defaults(func=command_transition)

    approve = sub.add_parser("approve")
    approve.add_argument("--project", required=True)
    approve.add_argument("--kind", choices=["copy", "voice", "edit_script", "upload"], required=True)
    approve.set_defaults(func=command_approve)

    reject = sub.add_parser("reject")
    reject.add_argument("--project", required=True)
    reject.add_argument("--kind", choices=["copy", "voice", "edit_script"], required=True)
    reject.add_argument("--reason", required=True)
    reject.set_defaults(func=command_reject)

    cover_choice = sub.add_parser("cover-choice")
    cover_choice.add_argument("--project", required=True)
    cover_choice.add_argument(
        "--choice", choices=["scrapbook", "user_provided"], required=True
    )
    cover_choice.set_defaults(func=command_cover_choice)

    artifact = sub.add_parser("artifact")
    artifact.add_argument("--project", required=True)
    artifact.add_argument("--name", required=True)
    artifact.add_argument("--path", required=True)
    artifact.set_defaults(func=command_artifact)

    block = sub.add_parser("block")
    block.add_argument("--project", required=True)
    block.add_argument("--reason", required=True)
    block.set_defaults(func=command_block)

    resume = sub.add_parser("resume")
    resume.add_argument("--project", required=True)
    resume.set_defaults(func=command_resume)

    published = sub.add_parser("published")
    published.add_argument("--project", required=True)
    published.add_argument("--platform", required=True)
    published.add_argument("--work-id", required=True)
    published.add_argument("--url", required=True)
    published.add_argument("--published-at")
    published.set_defaults(func=command_published)

    review = sub.add_parser("start-review")
    review.add_argument("--project", required=True)
    review.add_argument("--force-for-test", action="store_true")
    review.set_defaults(func=command_start_review)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        args.func(args)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
