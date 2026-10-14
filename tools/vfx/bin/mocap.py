"""Mocap department: markerless body motion capture from any normal video (MediaPipe).

Writes per-frame 3D landmarks (33 joints, metres, hip-centred) as JSON, plus
an optional overlay video for checking the track. Import the JSON into Blender
with blender_mocap_import.py.

  vfx-python mocap.py dance.mp4 dance_mocap.json --preview dance_track.mp4
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import torch
from mediapipe.tasks.python import BaseOptions, vision

sys.path.insert(0, str(Path(__file__).parent))
from _media import VideoWriter, probe_fps, read_frames  # noqa: E402

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
             "pose_landmarker_{v}/float16/latest/pose_landmarker_{v}.task")
CACHE = Path.home() / ".cache" / "vfx-studio"


def model_path(variant):
    path = CACHE / f"pose_landmarker_{variant}.task"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        torch.hub.download_url_to_file(MODEL_URL.format(v=variant), str(path))
    return str(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="video of one person")
    ap.add_argument("output", help="landmarks .json")
    ap.add_argument("--preview", help="optional overlay video .mp4")
    ap.add_argument("--quality", choices=["lite", "full", "heavy"], default="full")
    args = ap.parse_args()

    fps = probe_fps(args.input)
    landmarker = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path(args.quality)),
        running_mode=vision.RunningMode.VIDEO))
    names = [lm.name.lower() for lm in vision.PoseLandmark]
    bones = [(c.start, c.end) for c in vision.PoseLandmarksConnections.POSE_LANDMARKS]
    writer = VideoWriter(args.preview, fps) if args.preview else None

    frames = []
    for i, rgb in enumerate(read_frames(args.input)):
        res = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(i * 1000 / fps))
        if res.pose_world_landmarks:
            world = res.pose_world_landmarks[0]
            frames.append({"frame": i, "joints": [[p.x, p.y, p.z, p.visibility] for p in world]})
        else:
            frames.append({"frame": i, "joints": None})
        if writer:
            img = rgb.copy()
            if res.pose_landmarks:
                h, w = img.shape[:2]
                pts = [(int(p.x * w), int(p.y * h)) for p in res.pose_landmarks[0]]
                for a, b in bones:
                    cv2.line(img, pts[a], pts[b], (0, 255, 120), 3)
                for p in pts:
                    cv2.circle(img, p, 4, (255, 60, 60), -1)
            writer.write(img)
    if writer:
        writer.close()

    Path(args.output).write_text(json.dumps({"fps": fps, "joint_names": names, "frames": frames}))
    tracked = sum(f["joints"] is not None for f in frames)
    print(f"wrote {args.output}: {tracked}/{len(frames)} frames tracked")


if __name__ == "__main__":
    main()
