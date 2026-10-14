"""Upscale department: AI upscaling with Real-ESRGAN (via spandrel), CPU.

Slow on CPU (several seconds per 720p frame) - use for stills, short shots,
or test a few frames first with --frames.

  vfx-python upscale.py still.png still_4x.png
  vfx-python upscale.py shot.mp4 shot_2x.mp4 --scale 2 --frames 48
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from spandrel import ModelLoader

sys.path.insert(0, str(Path(__file__).parent))
from _media import VideoWriter, is_video, probe_fps, read_frames, write_image  # noqa: E402

MODELS = {
    "photo": ("RealESRGAN_x4plus.pth", "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"),
    "anime": ("RealESRGAN_x4plus_anime_6B.pth", "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"),
}
CACHE = Path.home() / ".cache" / "vfx-studio"


def load_model(kind):
    name, url = MODELS[kind]
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        torch.hub.download_url_to_file(url, str(path))
    return ModelLoader().load_from_file(str(path)).eval()


def tile_upscale(model, rgb, tile=256, pad=16):
    """Upscales in tiles so large frames fit in RAM."""
    s = model.scale
    h, w = rgb.shape[:2]
    x = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255).unsqueeze(0)
    out = torch.zeros(1, 3, h * s, w * s)
    with torch.inference_mode():
        for y0 in range(0, h, tile):
            for x0 in range(0, w, tile):
                ya, xa = max(y0 - pad, 0), max(x0 - pad, 0)
                yb, xb = min(y0 + tile + pad, h), min(x0 + tile + pad, w)
                piece = model(x[:, :, ya:yb, xa:xb])
                ty, tx = (y0 - ya) * s, (x0 - xa) * s
                th, tw = (min(y0 + tile, h) - y0) * s, (min(x0 + tile, w) - x0) * s
                out[:, :, y0 * s:y0 * s + th, x0 * s:x0 * s + tw] = piece[:, :, ty:ty + th, tx:tx + tw]
    return (out[0].permute(1, 2, 0).clamp(0, 1).mul(255).byte().numpy())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--scale", type=int, choices=[2, 4], default=4)
    ap.add_argument("--kind", choices=list(MODELS), default="photo")
    ap.add_argument("--frames", type=int, default=0, help="only process the first N frames (0 = all)")
    args = ap.parse_args()

    torch.set_num_threads(max(torch.get_num_threads(), 1))
    model = load_model(args.kind)
    video = is_video(args.input)
    writer = VideoWriter(args.output, probe_fps(args.input)) if video else None
    for i, rgb in enumerate(read_frames(args.input)):
        if args.frames and i >= args.frames:
            break
        out = tile_upscale(model, rgb)
        if args.scale != model.scale:
            h, w = rgb.shape[:2]
            out = cv2.resize(out, (w * args.scale, h * args.scale), interpolation=cv2.INTER_AREA)
        if writer:
            writer.write(out)
            print(f"frame {i}", flush=True)
        else:
            write_image(args.output, np.asarray(out))
    if writer:
        writer.close()
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
