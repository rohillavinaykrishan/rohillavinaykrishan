#!/usr/bin/env python3
"""Contact sheet: rows s0, s4, s12, s25, s38, s51 = full 2808 frame (scaled 0.5) | 100% crop on the monument.
Bottom strip: halo check, the held-out CG layer over black and over white at 100% (s25, s38) + the plate-only crop.
usage: sheet.py out.png [work_dir]"""
import sys, os, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
out = sys.argv[1]; wk = sys.argv[2] if len(sys.argv) > 2 else f'{ROOT}/comp/v001/work'
anc = json.load(open(f'{ROOT}/layout/v001/anchor.json'))['frames']
S = 2808 / 1280.0; CW, CH = 1100, 588
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 26)
except Exception: font = ImageFont.load_default()
FR = [0, 4, 12, 25, 38, 51]
rows = []
for i in FR:
    f = Image.open(f'{wk}/final/final.{i:04d}.png').convert('RGB')
    b = anc[i]['bbox']; cx, cy = (b[0] + b[2]) / 2 * S, (b[1] + b[3]) / 2 * S
    if i < 4: cy = anc[i]['centre_falling'][1] * S + 60
    x0 = int(np.clip(cx - CW / 2, 0, 2808 - CW)); y0 = int(np.clip(cy - CH / 2, 0, 1176 - CH))
    crop = f.crop((x0, y0, x0 + CW, y0 + CH))
    small = f.resize((1404, 588), Image.LANCZOS); d = ImageDraw.Draw(small)
    d.rectangle([x0 / 2, y0 / 2, (x0 + CW) / 2, (y0 + CH) / 2], outline=(255, 46, 136), width=2)
    d.text((14, 10), f's{i}  (f{169 + i})', fill=(255, 46, 136), font=font)
    row = Image.new('RGB', (1404 + 8 + CW, CH), (18, 16, 13)); row.paste(small, (0, 0)); row.paste(crop, (1412, 0))
    ImageDraw.Draw(row).text((1424, 10), '100%', fill=(255, 46, 136), font=font)
    rows.append(row)
# halo strip
strip = []
for i in (25, 38):
    p = f'{wk}/cglayer/cg.{i:04d}.png'
    if not os.path.exists(p): continue
    L = cv2.imread(p, -1)[..., [2, 1, 0, 3]].astype(np.float32) / 65535.0
    b = anc[i]['bbox']; cx, cy = (b[0] + b[2]) / 2 * S, (b[1] + b[3]) / 2 * S
    x0 = int(np.clip(cx - 300, 0, 2808 - 600)); y0 = int(np.clip(cy - 294, 0, 1176 - 588))
    c = L[y0:y0 + 588, x0:x0 + 600]
    for bgv, name in ((0.0, 'over black'), (1.0, 'over white')):
        im = c[..., :3] * c[..., 3:4] + bgv * (1 - c[..., 3:4])
        t = Image.fromarray((im * 255 + 0.5).astype(np.uint8)); ImageDraw.Draw(t).text((10, 8), f's{i} CG {name}', fill=(255, 46, 136), font=font)
        strip.append(t)
Wd = rows[0].width
sh = Image.new('RGB', (Wd, sum(r.height + 8 for r in rows) + (596 if strip else 0) + 50), (18, 16, 13))
ImageDraw.Draw(sh).text((14, 10), 'sh010 comp v001  final 2808x1176  rows: full frame (0.5x) | 100% crop   bottom: CG layer edge check 100%', fill=(242, 235, 223), font=font)
y = 50
for r in rows: sh.paste(r, (0, y)); y += r.height + 8
x = 0
for t in strip: sh.paste(t, (x, y)); x += t.width + 8
sh.save(out); print('wrote', out, sh.size)
