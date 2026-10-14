"""Roto department (precise): click-to-select any object and track it through a
shot with SAM 2. Use when rembg picks the wrong subject (a car, a guitar, one
dancer out of five...).

  vfx-python sam_roto.py shot.mp4 guitar.mov --point 640,360            # alpha cut-out
  vfx-python sam_roto.py shot.mp4 matte.mp4 --point 640,360 --point 700,500 --mode matte
  vfx-python sam_roto.py shot.mp4 m.mp4 --point 300,200 --neg 320,600 --frame 12
--point = on the object, --neg = NOT the object, --frame = frame the clicks refer to.
CPU speed: roughly 1-3 s per 720p frame with the tiny model.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch
from sam2.build_sam import build_sam2_video_predictor

sys.path.insert(0, str(Path(__file__).parent))
from _media import VideoWriter, probe_fps, read_frames  # noqa: E402

CKPT_URL = "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_{size}.pt"
CONFIG = "configs/sam2.1/sam2.1_hiera_{short}.yaml"
SIZES = {"tiny": "t", "small": "s", "base_plus": "b+", "large": "l"}
CACHE = Path.home() / ".cache" / "vfx-studio"


def xy(s):
    x, y = s.split(",")
    return [float(x), float(y)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="video")
    ap.add_argument("output", help=".mov (alpha) or .mp4 (matte/green)")
    ap.add_argument("--point", type=xy, action="append", required=True, help="x,y on the object (pixels)")
    ap.add_argument("--neg", type=xy, action="append", default=[], help="x,y NOT on the object")
    ap.add_argument("--frame", type=int, default=0)
    ap.add_argument("--mode", choices=["alpha", "matte", "green"], default="alpha")
    ap.add_argument("--size", choices=list(SIZES), default="tiny")
    args = ap.parse_args()

    ckpt = CACHE / f"sam2.1_hiera_{args.size}.pt"
    if not ckpt.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        torch.hub.download_url_to_file(CKPT_URL.format(size=args.size), str(ckpt))
    predictor = build_sam2_video_predictor(CONFIG.format(short=SIZES[args.size]), str(ckpt), device="cpu")

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-i", args.input, "-q:v", "2",
                        "-start_number", "0", f"{tmp}/%05d.jpg"], check=True)
        with torch.inference_mode():
            state = predictor.init_state(video_path=tmp)
            pts = np.array(args.point + args.neg, dtype=np.float32)
            labels = np.array([1] * len(args.point) + [0] * len(args.neg), dtype=np.int32)
            predictor.add_new_points_or_box(state, frame_idx=args.frame, obj_id=1, points=pts, labels=labels)
            masks = {}
            for reverse in ([False, True] if args.frame > 0 else [False]):
                for idx, _, logits in predictor.propagate_in_video(state, start_frame_idx=args.frame, reverse=reverse):
                    masks[idx] = (logits[0, 0] > 0).numpy()
                    if idx % 10 == 0:
                        print(f"tracked frame {idx}", flush=True)

    writer = VideoWriter(args.output, probe_fps(args.input))
    for i, rgb in enumerate(read_frames(args.input)):
        alpha = masks.get(i, np.zeros(rgb.shape[:2], bool)).astype(np.uint8) * 255
        if args.mode == "alpha":
            out = np.dstack([rgb, alpha])
        elif args.mode == "matte":
            out = np.dstack([alpha] * 3)
        else:
            a = alpha[..., None] / 255.0
            out = (rgb * a + np.array([0, 177, 64]) * (1 - a)).astype(np.uint8)
        writer.write(out)
    writer.close()
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
