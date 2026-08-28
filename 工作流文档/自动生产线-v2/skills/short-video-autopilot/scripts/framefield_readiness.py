#!/usr/bin/env python3
"""Verify the isolated FrameField session and prewarm proxies used by its timeline."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def read_json(url: str, timeout: float) -> dict:
    with urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def web_reachable(url: str, timeout: float) -> bool:
    try:
        with urlopen(url, timeout=timeout):
            return True
    except HTTPError:
        return True
    except URLError:
        return False


def used_video_assets(project: dict) -> list[dict]:
    used_ids: list[str] = []
    for track in project.get("tracks", []):
        if track.get("kind") not in {"video", "overlay"}:
            continue
        for item in track.get("items", []):
            asset_id = item.get("assetId")
            if asset_id and asset_id not in used_ids:
                used_ids.append(asset_id)
    by_id = {asset.get("id"): asset for asset in project.get("assets", [])}
    return [by_id[asset_id] for asset_id in used_ids if by_id.get(asset_id, {}).get("kind") == "video"]


def request_proxy(api: str, asset_id: str, timeout: float) -> None:
    query = urlencode({"id": asset_id})
    with urlopen(f"{api}/api/proxy?{query}", timeout=timeout) as response:
        response.read(1)


def write_report(
    output: Path,
    mode: str,
    api: str,
    web: str,
    health: dict,
    project: dict,
    expected_project_file: Path,
    assets: list[dict],
) -> None:
    marker = "帧场剪辑就绪：通过" if mode == "edit" else "帧场预览就绪：通过"
    lines = [
        f"# {marker}",
        "",
        f"- 检查时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- 模式：{mode}",
        f"- API：{api}",
        f"- 界面：{web}",
        f"- 工程文件：{expected_project_file}",
        f"- 工程修订：{int(project.get('revision', 0))}",
        f"- 在用视频代理：{len(assets)}/{len(assets)}",
        f"- 播放头：{int(project.get('playheadFrame', 0))}",
        f"- 硬件编码器：{health.get('hardwareEncoder')}",
        "",
        "## 在用素材",
        "",
    ]
    lines.extend(f"- `{asset.get('id')}` {asset.get('name')}" for asset in assets)
    if not assets:
        lines.append("- 当前时间线尚无视频素材")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="帧场会话、工程与代理就绪检查")
    parser.add_argument("--project", required=True, help="自动生产线运行项目目录")
    parser.add_argument("--mode", choices=["edit", "preview"], required=True)
    parser.add_argument("--api-port", type=int, default=4318)
    parser.add_argument("--web-port", type=int, default=3001)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--output")
    args = parser.parse_args()

    run_project = Path(args.project).expanduser().resolve()
    state_file = run_project / "pipeline-state.json"
    framefield_dir = run_project / "framefield"
    expected_project_file = (framefield_dir / "project.json").resolve()
    if not state_file.is_file() or not expected_project_file.is_file():
        raise ValueError("运行项目状态或帧场工程不存在")

    state = json.loads(state_file.read_text(encoding="utf-8"))
    if state.get("confirmations", {}).get("edit_script") != "approved":
        raise ValueError("剪辑脚本尚未确认，禁止准备帧场")
    if state.get("stage") not in {"editing_framefield", "validating"}:
        raise ValueError(f"当前状态不能准备帧场：{state.get('stage')}")

    api = f"http://127.0.0.1:{args.api_port}"
    web = f"http://127.0.0.1:{args.web_port}/"
    health = read_json(f"{api}/api/health", min(args.timeout, 15))
    actual_project_file = Path(health.get("projectFile", "")).expanduser().resolve()
    if actual_project_file != expected_project_file:
        raise ValueError(f"帧场连接了错误工程：{actual_project_file}；应为：{expected_project_file}")
    if int(health.get("port", -1)) != args.api_port:
        raise ValueError("帧场API端口与当前项目配置不一致")
    if not web_reachable(web, min(args.timeout, 15)):
        raise ValueError(f"帧场界面不可用：{web}")

    project = read_json(f"{api}/api/project", min(args.timeout, 15))
    assets = used_video_assets(project)
    if args.mode == "preview" and not assets:
        raise ValueError("时间线没有在用视频，不能进入预览")

    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 3))) as executor:
        jobs = {
            executor.submit(request_proxy, api, asset["id"], args.timeout): asset
            for asset in assets
        }
        for future in as_completed(jobs):
            asset = jobs[future]
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001 - report every failed asset together
                failures.append(f"{asset.get('name')}: {exc}")
    if failures:
        raise ValueError("代理生成失败：" + "；".join(failures))

    cache_dir = Path(health.get("cacheDir", "")).expanduser().resolve()
    missing = [
        asset.get("name", asset["id"])
        for asset in assets
        if not (cache_dir / "proxies" / f"{asset['id']}.mp4").is_file()
        or (cache_dir / "proxies" / f"{asset['id']}.mp4").stat().st_size == 0
    ]
    if missing:
        raise ValueError("代理文件未就绪：" + "、".join(missing))
    if args.mode == "preview" and int(project.get("playheadFrame", 0)) != 0:
        raise ValueError("交付预览前必须把播放头归零")

    default_name = "framefield-edit-ready.md" if args.mode == "edit" else "framefield-preview-ready.md"
    output = Path(args.output).expanduser().resolve() if args.output else run_project / default_name
    write_report(output, args.mode, api, web, health, project, expected_project_file, assets)
    print(json.dumps({
        "ready": True,
        "mode": args.mode,
        "project_file": str(expected_project_file),
        "revision": int(project.get("revision", 0)),
        "proxy_count": len(assets),
        "report": str(output),
        "web": web,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, URLError, json.JSONDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(2)
