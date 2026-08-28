#!/usr/bin/env python3
"""Detect shot rhythm for short sales videos.

Requires PySceneDetect for true cut detection:
  python -m pip install scenedetect[opencv]
Falls back to fixed 2-second beats if PySceneDetect is unavailable.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_json(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def ffprobe_duration(video: Path) -> float:
    data = run_json([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(video)
    ])
    return float(data.get("format", {}).get("duration") or 0)


def fixed_scenes(duration: float, seconds: float = 2.0) -> list[dict]:
    scenes = []
    start = 0.0
    idx = 1
    while start < duration:
        end = min(duration, start + seconds)
        scenes.append({"scene": idx, "start": round(start, 3), "end": round(end, 3), "duration": round(end - start, 3), "method": "fixed_fallback"})
        start = end
        idx += 1
    return scenes


def detect_with_pyscenedetect(video: Path) -> list[dict]:
    from scenedetect import ContentDetector, SceneManager, open_video

    stream = open_video(str(video))
    manager = SceneManager()
    manager.add_detector(ContentDetector())
    manager.detect_scenes(stream)
    scene_list = manager.get_scene_list()

    scenes = []
    for idx, (start, end) in enumerate(scene_list, start=1):
        start_s = start.get_seconds()
        end_s = end.get_seconds()
        scenes.append({
            "scene": idx,
            "start": round(start_s, 3),
            "end": round(end_s, 3),
            "duration": round(end_s - start_s, 3),
            "method": "pyscenedetect_content",
        })
    return scenes


def make_clips(video: Path, clips_dir: Path, scenes: list[dict]) -> None:
    clips_dir.mkdir(parents=True, exist_ok=True)
    for scene in scenes:
        out = clips_dir / f"scene_{scene['scene']:03d}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", str(scene["start"]),
            "-to", str(scene["end"]), "-i", str(video), "-c", "copy", str(out)
        ], check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Analysis folder, e.g. 视频分析/日期_名称")
    parser.add_argument("--make-clips", action="store_true")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(args.video)
    warning = None
    try:
        scenes = detect_with_pyscenedetect(args.video)
        if not scenes:
            scenes = fixed_scenes(duration)
            warning = "PySceneDetect returned no scenes; used fixed 2-second fallback."
    except Exception as exc:
        scenes = fixed_scenes(duration)
        warning = f"PySceneDetect unavailable or failed; used fallback. Detail: {exc}"

    if args.make_clips:
        make_clips(args.video, args.out / "clips", scenes)

    metrics = {
        "video": str(args.video),
        "duration": round(duration, 3),
        "scene_count": len(scenes),
        "average_scene_duration": round(sum(s["duration"] for s in scenes) / len(scenes), 3) if scenes else 0,
        "warning": warning,
        "scenes": scenes,
    }
    (args.out / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
