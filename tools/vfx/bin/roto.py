"""Roto department: AI background removal for an image or video (rembg).

  vfx-python roto.py in.mp4 out.mov                  # ProRes 4444 with alpha
  vfx-python roto.py in.mp4 out.mp4 --mode green     # subject on green screen
  vfx-python roto.py in.mp4 matte.mp4 --mode matte   # black/white matte for comp
  vfx-python roto.py photo.jpg cutout.png --model u2net_human_seg
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from rembg import new_session, remove

sys.path.insert(0, str(Path(__file__).parent))
from _media import VideoWriter, is_video, probe_fps, read_frames, write_image  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--mode", choices=["alpha", "matte", "green"], default="alpha")
    ap.add_argument("--model", default="isnet-general-use",
                    help="u2net | isnet-general-use | u2net_human_seg | birefnet-general (best, slowest)")
    args = ap.parse_args()

    session = new_session(args.model)
    writer = VideoWriter(args.output, probe_fps(args.input)) if is_video(args.input) else None
    for i, rgb in enumerate(read_frames(args.input)):
        alpha = remove(rgb, session=session, only_mask=True)
        alpha = np.asarray(alpha, dtype=np.uint8)
        if args.mode == "alpha":
            out = np.dstack([rgb, alpha])
        elif args.mode == "matte":
            out = np.dstack([alpha] * 3)
        else:
            a = alpha[..., None].astype(np.float32) / 255
            out = (rgb * a + np.array([0, 177, 64]) * (1 - a)).astype(np.uint8)
        if writer:
            writer.write(out)
            if i % 25 == 0:
                print(f"frame {i}", flush=True)
        else:
            write_image(args.output, out)
    if writer:
        writer.close()
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
