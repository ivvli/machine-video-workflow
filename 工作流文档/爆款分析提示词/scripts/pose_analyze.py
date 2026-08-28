#!/usr/bin/env python3
"""Sample MediaPipe body/hand/face evidence from a short video.

This is intentionally coarse. It provides evidence for later human/Codex judgment,
not final body-language interpretation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--sample-fps", type=float, default=2.0)
    args = parser.parse_args()

    try:
        import cv2
        import mediapipe as mp
    except Exception as exc:
        result = {
            "video": str(args.video),
            "warning": f"mediapipe/cv2 unavailable; install mediapipe and opencv-python. Detail: {exc}",
            "samples": [],
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    cap = cv2.VideoCapture(str(args.video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_step = max(1, int(round(fps / args.sample_fps)))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    if not hasattr(mp, "solutions"):
        result = {
            "video": str(args.video),
            "warning": "Installed MediaPipe does not expose the legacy mp.solutions API used by this lightweight sampler. The skill can still use scene/keyframe evidence; install a legacy-compatible mediapipe build or extend this script to the Tasks API for pose metrics.",
            "samples": [],
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    mp_pose = mp.solutions.pose
    mp_hands = mp.solutions.hands
    mp_face = mp.solutions.face_detection

    samples = []
    try:
        with mp_pose.Pose(static_image_mode=False, model_complexity=1) as pose, \
             mp_hands.Hands(static_image_mode=False, max_num_hands=2) as hands, \
             mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face:
            frame_index = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if frame_index % frame_step == 0:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pose_result = pose.process(rgb)
                    hands_result = hands.process(rgb)
                    face_result = face.process(rgb)
                    t = frame_index / fps
                    samples.append({
                        "time": round(t, 3),
                        "person_pose_detected": bool(pose_result.pose_landmarks),
                        "hand_count": len(hands_result.multi_hand_landmarks or []),
                        "face_detected": bool(face_result.detections),
                    })
                frame_index += 1
    except Exception as exc:
        cap.release()
        result = {
            "video": str(args.video),
            "warning": f"MediaPipe runtime failed; on macOS this can happen inside a sandbox without GL context. Try rerunning outside the sandbox. Detail: {exc}",
            "samples": [],
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    cap.release()
    person_samples = sum(1 for s in samples if s["person_pose_detected"])
    hand_samples = sum(1 for s in samples if s["hand_count"] > 0)
    face_samples = sum(1 for s in samples if s["face_detected"])
    result = {
        "video": str(args.video),
        "fps": fps,
        "total_frames": total_frames,
        "sample_count": len(samples),
        "person_presence_ratio": round(person_samples / len(samples), 3) if samples else 0,
        "hand_presence_ratio": round(hand_samples / len(samples), 3) if samples else 0,
        "face_presence_ratio": round(face_samples / len(samples), 3) if samples else 0,
        "samples": samples,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
