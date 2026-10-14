"""Depth department: "AI LiDAR" from a single photo (Depth Anything V2 Small,
Apache-2.0 - free for commercial use) and 3D parallax camera moves on stills.

  vfx-python depth.py map photo.jpg depth.png               # 16-bit depth (white = near) + _preview.jpg
  vfx-python depth.py parallax photo.jpg move.mp4 --move dolly-in --dur 5
  vfx-python depth.py parallax photo.jpg move.mp4 --move orbit --size 3840x2160 --amount 1.2
  vfx-python depth.py map source/images/ depth_maps/        # whole folder

Moves: dolly-in, dolly-out, orbit, pan-left, pan-right, rise, drift (slow, for verses).
The near/far depth map is also what the compositor uses to put fog, light rays and
particles BETWEEN the subject and the background.
"""
import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

MODEL = "depth-anything/Depth-Anything-V2-Small-hf"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


class Depth:
    def __init__(self):
        self.proc = AutoImageProcessor.from_pretrained(MODEL)
        self.model = AutoModelForDepthEstimation.from_pretrained(MODEL).eval()

    def __call__(self, rgb):
        """Relative depth, 0 = far .. 1 = near, same size as the image."""
        inputs = self.proc(images=Image.fromarray(rgb), return_tensors="pt")
        with torch.inference_mode():
            pred = self.model(**inputs).predicted_depth  # inverse depth: bigger = nearer
        d = torch.nn.functional.interpolate(pred[None], size=rgb.shape[:2], mode="bicubic",
                                            align_corners=False)[0, 0].numpy()
        lo, hi = np.percentile(d, 1), np.percentile(d, 99)
        return np.clip((d - lo) / (hi - lo + 1e-6), 0, 1).astype(np.float32)


def read_rgb(path):
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise SystemExit(f"cannot read {path}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def save_map(depth, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), (depth * 65535).astype(np.uint16))
    preview = cv2.applyColorMap((depth * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    cv2.imwrite(str(out.with_name(out.stem + "_preview.jpg")), preview, [cv2.IMWRITE_JPEG_QUALITY, 90])


def camera(move, t, amount):
    """(shift_x, shift_y, zoom) of the virtual camera at progress t in [0, 1]."""
    e = t * t * (3 - 2 * t)  # ease in-out
    a = amount
    return {
        "dolly-in": (0.0, 0.0, 1 + 0.10 * a * e),
        "dolly-out": (0.0, 0.0, 1 + 0.10 * a * (1 - e)),
        "orbit": (0.035 * a * np.sin(2 * np.pi * t), 0.008 * a * np.sin(4 * np.pi * t), 1.02),
        "pan-left": (0.04 * a * (0.5 - e), 0.0, 1.03),
        "pan-right": (0.04 * a * (e - 0.5), 0.0, 1.03),
        "rise": (0.0, 0.03 * a * (0.5 - e), 1.03),
        "drift": (0.015 * a * (e - 0.5), 0.006 * a * (0.5 - e), 1 + 0.03 * a * e),
    }[move]


def parallax(rgb, depth, out, move, dur, fps, size, amount, focus):
    """2.5D camera move: near pixels move more than far ones. A backward warp
    (each output pixel looks up where it came from) keeps it hole-free; a small
    overscan hides the edges."""
    ow, oh = size
    # cover-crop the photo + depth to the output aspect with 12% overscan
    h, w = rgb.shape[:2]
    s = max(ow / w, oh / h) * 1.12
    rgb = cv2.resize(rgb, (int(w * s), int(h * s)), interpolation=cv2.INTER_LANCZOS4)
    depth = cv2.resize(depth, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
    depth = cv2.GaussianBlur(depth, (0, 0), 3)  # soft depth edges = fewer tearing artifacts
    H, W = rgb.shape[:2]
    yy, xx = np.mgrid[0:oh, 0:ow].astype(np.float32)
    cx, cy = W / 2, H / 2
    rel = depth - focus  # parallax relative to the focus plane (0.5 = mid-ground stays put)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}",
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(dur * fps))
    for i in range(n):
        sx, sy, zoom = camera(move, i / max(n - 1, 1), amount)
        # base sampling grid: output pixel -> source pixel at the current zoom
        bx = cx + (xx - ow / 2) / zoom
        by = cy + (yy - oh / 2) / zoom
        d = cv2.remap(rel, bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        dz = (zoom - 1) * 0.6  # dolly: near things grow faster than far ones
        mx = bx - sx * W * d - (bx - cx) * dz * d
        my = by - sy * H * d - (by - cy) * dz * d
        frame = cv2.remap(rgb, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REFLECT)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("map")
    m.add_argument("input", help="image or folder")
    m.add_argument("output", help="depth .png or folder")
    p = sub.add_parser("parallax")
    p.add_argument("input")
    p.add_argument("output", help=".mp4")
    p.add_argument("--move", default="dolly-in",
                   choices=["dolly-in", "dolly-out", "orbit", "pan-left", "pan-right", "rise", "drift"])
    p.add_argument("--dur", type=float, default=5.0)
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--size", default="1920x1080", help="WxH; 3840x2160 for native 4K, 1080x1920 vertical")
    p.add_argument("--amount", type=float, default=1.0, help="strength of the move (0.5 subtle .. 2 strong)")
    p.add_argument("--focus", type=float, default=0.5, help="depth that stays still (0 far .. 1 near)")
    p.add_argument("--depth", help="reuse a saved depth .png instead of computing it")
    args = ap.parse_args()

    torch.set_num_threads(max(torch.get_num_threads(), 1))
    if args.cmd == "map":
        src = Path(args.input)
        files = sorted(f for f in src.iterdir() if f.suffix.lower() in IMAGE_EXTS) if src.is_dir() else [src]
        est = Depth()
        for f in files:
            dst = Path(args.output) / (f.stem + "_depth.png") if src.is_dir() else Path(args.output)
            save_map(est(read_rgb(f)), dst)
            print(f"wrote {dst}", flush=True)
        return

    rgb = read_rgb(args.input)
    if args.depth:
        depth = cv2.imread(args.depth, cv2.IMREAD_UNCHANGED).astype(np.float32)
        depth = cv2.resize(depth / depth.max(), (rgb.shape[1], rgb.shape[0]))
    else:
        depth = Depth()(rgb)
    w, h = map(int, args.size.split("x"))
    parallax(rgb, depth, args.output, args.move, args.dur, args.fps, (w, h), args.amount, args.focus)
    print(f"wrote {args.output} ({w}x{h}, {args.dur}s, {args.move})")


if __name__ == "__main__":
    main()
