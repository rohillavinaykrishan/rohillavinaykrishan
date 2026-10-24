#!/usr/bin/env python3
"""Before/after 100% crops: comp v001 (left) vs v002 (right) on s4, s23, s31; crop on the monument + nearby fighters."""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
anc = json.load(open(f'{ROOT}/layout/v001/anchor.json'))['frames']; S = 2808 / 1280.0; CW, CH = 1250, 640
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 28)
rows = []
for i in (4, 23, 31):
    b = anc[i]['bbox']; cx, cy = (b[0] + b[2]) / 2 * S - 250, (b[1] + b[3]) / 2 * S + 60
    x0 = int(np.clip(cx - CW / 2, 0, 2808 - CW)); y0 = int(np.clip(cy - CH / 2, 0, 1176 - CH))
    row = Image.new('RGB', (2 * CW + 10, CH), (18, 16, 13))
    for k, v in enumerate(('v001', 'v002')):
        im = Image.open(f'{ROOT}/comp/{v}/work/final/final.{i:04d}.png').convert('RGB').crop((x0, y0, x0 + CW, y0 + CH))
        ImageDraw.Draw(im).text((12, 10), f'{v}  s{i} (f{169 + i})  100%', fill=(255, 46, 136), font=font)
        row.paste(im, (k * (CW + 10), 0))
    rows.append(row)
sh = Image.new('RGB', (rows[0].width, len(rows) * (CH + 10) + 50), (18, 16, 13))
ImageDraw.Draw(sh).text((12, 10), 'sh010 comp v001 (left) vs v002 (right): grid-aligned deblock + hqdn3d at 1280x536 before the upscale', fill=(242, 235, 223), font=font)
for k, r in enumerate(rows): sh.paste(r, (0, 50 + k * (CH + 10)))
sh.save(sys.argv[1]); print('wrote', sys.argv[1], sh.size)
