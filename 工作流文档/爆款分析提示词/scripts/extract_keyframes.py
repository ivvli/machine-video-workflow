#!/usr/bin/env python3
"""Extract keyframes for visual reverse-analysis with FFmpeg."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--every", type=float, default=1.0, help="Seconds between frames for the coarse pass; add scene-start/action-boundary frames separately")
    parser.add_argument("--width", type=int, default=720)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    pattern = args.out / "frame_%03d.jpg"
    vf = f"fps=1/{args.every},scale={args.width}:-1"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(args.video), "-vf", vf, "-q:v", "2", str(pattern)], check=True)

    frames = sorted(args.out.glob("frame_*.jpg"))
    manifest = {
        "video": str(args.video),
        "interval_seconds": args.every,
        "frame_count": len(frames),
        "frames": [str(p) for p in frames],
    }
    (args.out / "keyframes.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
