#!/usr/bin/env python3
"""Bone SF logo: luminance texture (high-pass) mapped Umber->Bone, alpha kept. 2160 px wide."""
import sys, numpy as np
from PIL import Image, ImageFilter
src, out, W = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2160
UMBER = np.array([0x3A, 0x2E, 0x24], float); BONE = np.array([0xF2, 0xEB, 0xDF], float)
im = Image.open(src).convert("RGBA")
H = round(im.height * W / im.width)
im = im.resize((W, H), Image.LANCZOS)  # PIL resizes RGBA premultiplied -> no dark fringes
a = np.asarray(im).astype(float)
al = a[..., 3] / 255.0
L = a[..., :3] @ np.array([0.2126, 0.7152, 0.0722])
# remove the yellow->red gradient (low freq), keep the brush texture (high freq)
Lw = L * al
def blur(x, f=24):  # low-pass via BOX downscale + bicubic upscale (PIL 'F' mode has no gaussian)
    im_ = Image.fromarray(x.astype(np.float32), "F")
    sm = im_.resize((max(1, x.shape[1] // f), max(1, x.shape[0] // f)), Image.BOX)
    return np.asarray(sm.resize((x.shape[1], x.shape[0]), Image.BICUBIC))
low = blur(Lw) / np.maximum(blur(al), 1e-3)
detail = (L - low) / 255.0
t = np.clip(0.90 + 1.6 * detail, 0, 1)
e = np.clip((al - 0.55) / 0.40, 0, 1)   # soft edges -> pure Bone (source edge pixels are dark)
t = t * e + (1 - e)
t = np.where(al > 0.02, t, 1.0)          # transparent RGB = Bone (no fringe if unpremultiplied)
rgb = UMBER + t[..., None] * (BONE - UMBER)
alpha = np.clip(np.round(al * 255), 0, 255)
alpha[alpha < 3] = 0                      # kill near-zero speckle
outa = np.dstack([rgb, alpha]).round().clip(0, 255).astype(np.uint8)
Image.fromarray(outa, "RGBA").save(out, optimize=True)
print(out, outa.shape)
