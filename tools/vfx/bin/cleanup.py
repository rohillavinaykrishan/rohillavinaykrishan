"""Paint/Prep department: remove wires, logos, people or objects (LaMa inpainting).

The mask is white where things should be removed. Give either a mask image
(static, reused on every frame) or a box.

  vfx-python cleanup.py plate.mp4 clean.mp4 --mask mask.png
  vfx-python cleanup.py photo.jpg clean.png --box 120,80,300,260   # x1,y1,x2,y2
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from simple_lama_inpainting.models.model import LAMA_MODEL_URL
from simple_lama_inpainting.utils import download_model, prepare_img_and_mask

sys.path.insert(0, str(Path(__file__).parent))
from _media import VideoWriter, is_video, probe_fps, read_frames, write_image  # noqa: E402


class Lama:
    """simple-lama's own loader assumes CUDA; this one maps the model to CPU."""

    def __init__(self):
        self.model = torch.jit.load(download_model(LAMA_MODEL_URL), map_location="cpu").eval()

    def __call__(self, image, mask):
        image, mask = prepare_img_and_mask(image, mask, torch.device("cpu"))
        with torch.inference_mode():
            out = self.model(image, mask)[0].permute(1, 2, 0).numpy()
        return np.clip(out * 255, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--mask", help="white = remove")
    g.add_argument("--box", help="x1,y1,x2,y2 region to remove")
    ap.add_argument("--grow", type=int, default=8, help="expand mask by N px to hide edges")
    args = ap.parse_args()

    lama = Lama()
    video = is_video(args.input)
    writer = VideoWriter(args.output, probe_fps(args.input), audio_from=args.input) if video else None
    mask = None
    for i, rgb in enumerate(read_frames(args.input)):
        h, w = rgb.shape[:2]
        if mask is None:
            if args.mask:
                mask = cv2.resize(cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE), (w, h))
            else:
                x1, y1, x2, y2 = map(int, args.box.split(","))
                mask = np.zeros((h, w), np.uint8)
                mask[y1:y2, x1:x2] = 255
            mask = (mask > 127).astype(np.uint8) * 255
            if args.grow:
                mask = cv2.dilate(mask, np.ones((args.grow * 2 + 1,) * 2, np.uint8))
        out = np.asarray(lama(Image.fromarray(rgb), Image.fromarray(mask)))[:h, :w]
        if writer:
            writer.write(out)
            if i % 10 == 0:
                print(f"frame {i}", flush=True)
        else:
            write_image(args.output, out)
    if writer:
        writer.close()
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
