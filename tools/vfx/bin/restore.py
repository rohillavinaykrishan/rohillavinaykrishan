"""Restoration department: make weak photos 4K-ready.

denoise (OpenCV) -> AI upscale (Real-ESRGAN) until the long side reaches
--target -> face restoration (GFPGAN) on every detected face, blended back
with a feathered mask. Works on single images or whole folders.

  vfx-python restore.py old_photo.jpg fixed.png
  vfx-python restore.py source/images/ restored/ --target 3840
  vfx-python restore.py selfie.jpg out.png --no-upscale --face-strength 0.6
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from spandrel import ModelLoader

sys.path.insert(0, str(Path(__file__).parent))
from upscale import load_model as load_esrgan, tile_upscale  # noqa: E402

CACHE = Path.home() / ".cache" / "vfx-studio"
GFPGAN_URL = "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"
FACE_URL = ("https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/"
            "face_detection_yunet/face_detection_yunet_2023mar.onnx")
# GFPGAN's 512x512 FFHQ alignment template: eye (image-left), eye, nose, mouth corners.
FFHQ_5PT = np.array([[192.98, 239.95], [318.90, 240.19], [256.63, 314.02],
                     [201.26, 371.41], [313.09, 371.15]], np.float32)
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def fetch(url):
    path = CACHE / url.rsplit("/", 1)[1]
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        torch.hub.download_url_to_file(url, str(path))
    return str(path)


class Restorer:
    def __init__(self, upscale):
        self.esrgan = load_esrgan("photo") if upscale else None
        self.gfpgan = ModelLoader().load_from_file(fetch(GFPGAN_URL)).eval()
        self.faces = cv2.FaceDetectorYN.create(fetch(FACE_URL), "", (320, 320), 0.7, 0.3, 5000)

    def detect(self, rgb):
        """Faces from OpenCV YuNet (also finds small faces in wide shots): rows of
        [x, y, w, h, 5 landmark (x, y) pairs, score] in full-image pixels."""
        h, w = rgb.shape[:2]
        s = min(1.0, 2048 / max(h, w))
        img = cv2.resize(rgb, (int(w * s), int(h * s))) if s < 1 else rgb
        self.faces.setInputSize((img.shape[1], img.shape[0]))
        _, found = self.faces.detect(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return [] if found is None else [np.concatenate([f[:14] / s, f[14:]]) for f in found]

    def restore_faces(self, rgb, strength):
        """GFPGAN on each frontal face: align to the FFHQ 5-point template, restore at
        512x512, warp back and blend with a feathered mask. Profile faces are skipped -
        GFPGAN distorts faces it can't align."""
        out = rgb.astype(np.float32)
        h, w = rgb.shape[:2]
        done = 0
        for f in self.detect(rgb):
            pts = f[4:14].reshape(5, 2).astype(np.float32)
            eye_dist = np.linalg.norm(pts[0] - pts[1])
            if eye_dist < 0.3 * f[2] or eye_dist < 8:  # side profile, or too tiny to help
                continue
            M, _ = cv2.estimateAffinePartial2D(pts, FFHQ_5PT, method=cv2.LMEDS)
            if M is None:
                continue
            face = cv2.warpAffine(rgb, M, (512, 512), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            t = torch.from_numpy(face).permute(2, 0, 1).float().div(255).unsqueeze(0)
            with torch.inference_mode():
                fixed = self.gfpgan(t)[0].permute(1, 2, 0).clamp(0, 1).mul(255).numpy()
            inv = cv2.invertAffineTransform(M)
            back = cv2.warpAffine(fixed, inv, (w, h), flags=cv2.INTER_CUBIC)
            mask = np.zeros((512, 512), np.float32)
            cv2.ellipse(mask, (256, 290), (170, 215), 0, 0, 360, 1, -1)
            mask = cv2.GaussianBlur(mask, (0, 0), 25)
            mask = cv2.warpAffine(mask, inv, (w, h))[..., None] * strength
            out = out * (1 - mask) + back * mask
            done += 1
        return out.clip(0, 255).astype(np.uint8), done

    def run(self, rgb, target, denoise, strength):
        if denoise:
            rgb = cv2.fastNlMeansDenoisingColored(rgb, None, denoise, denoise, 7, 21)
        while self.esrgan is not None and max(rgb.shape[:2]) < target * 0.9:
            rgb = tile_upscale(self.esrgan, rgb)
        if max(rgb.shape[:2]) > target:
            s = target / max(rgb.shape[:2])
            rgb = cv2.resize(rgb, (int(rgb.shape[1] * s), int(rgb.shape[0] * s)), interpolation=cv2.INTER_AREA)
        return self.restore_faces(rgb, strength) if strength > 0 else (rgb, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="image or folder")
    ap.add_argument("output", help="image or folder")
    ap.add_argument("--target", type=int, default=3840, help="long side in px after upscaling (default 4K)")
    ap.add_argument("--no-upscale", action="store_true")
    ap.add_argument("--denoise", type=int, default=3, help="0 = off; 3-6 for phone noise, 8-12 for old scans")
    ap.add_argument("--face-strength", type=float, default=0.5, help="0 = off, 1 = full; always compare with 0 and keep the more natural one")
    args = ap.parse_args()

    src = Path(args.input)
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in IMAGE_EXTS) if src.is_dir() else [src]
    out_dir = Path(args.output) if src.is_dir() else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    torch.set_num_threads(max(torch.get_num_threads(), 1))
    r = Restorer(upscale=not args.no_upscale)
    for f in files:
        bgr = cv2.imread(str(f), cv2.IMREAD_COLOR)
        if bgr is None:
            print(f"skip {f} (unreadable)")
            continue
        rgb, n = r.run(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), args.target, args.denoise, args.face_strength)
        dst = out_dir / (f.stem + ".png") if out_dir else Path(args.output)
        cv2.imwrite(str(dst), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        print(f"{f.name}: {bgr.shape[1]}x{bgr.shape[0]} -> {rgb.shape[1]}x{rgb.shape[0]}, {n} frontal face(s) restored", flush=True)


if __name__ == "__main__":
    main()
