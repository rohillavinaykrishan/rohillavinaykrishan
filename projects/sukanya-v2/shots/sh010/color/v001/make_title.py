#!/usr/bin/env python3
"""Title look (treatment 5.4): line-up art -> title_lineup tritone (alpha kept);
SF logo -> logo_gold (burnt saffron -> Saffron -> Ki White) + 6% highlight bloom (alpha kept).
ffmpeg equivalent for the line-up: lut3d=file=title_lineup.cube:interp=tetrahedral (alpha passes through)."""
import os, numpy as np
from PIL import Image, ImageFilter
import make_luts as ML
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(H, '../../../../assets_prev')
def run(src, fn, dst, bloom=0.0):
    im = np.asarray(Image.open(src).convert('RGBA')) / 255.0
    rgb, a = im[..., :3], im[..., 3:]
    out = fn(rgb.reshape(-1, 3)).reshape(rgb.shape)
    if bloom:
        hi = np.clip((ML.luma709(out) - 0.75) / 0.25, 0, 1)[..., None] * out * a
        bl = np.asarray(Image.fromarray((hi * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))) / 255.0
        out = 1 - (1 - out) * (1 - bloom * bl)                 # screen at 6%
        a = np.maximum(a, bloom * ML.luma709(bl)[..., None])   # glow may spill just past the edge
    Image.fromarray((np.concatenate([np.clip(out, 0, 1), a], -1) * 255 + 0.5).astype(np.uint8)).save(dst)
    print('wrote', dst)
run(os.path.join(P, 'lineup_restored_2160_r470.png'), ML.title_lineup, os.path.join(H, 'title/lineup_tritone.png'))
run(os.path.join(P, 'sf_logo_alpha.png'), ML.logo_gold, os.path.join(H, 'title/sf_logo_gold.png'), bloom=0.06)
