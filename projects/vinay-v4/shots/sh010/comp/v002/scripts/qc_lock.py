#!/usr/bin/env python3
"""Lock QC: plinth front base corners measured in the comp's CG alpha (distorted, 2808) vs layout anchor.json.
Reported in plate px (1280). Measures the bottom edge y under each corner (robust to horizontal motion blur)
and the outer x of the plinth at the corner row (alpha 0.5 contour). Residual = measured - anchor.
'Slide' = residual minus its median over s4-s43 (the constant part is the plinth bevel / pixel-centre convention)."""
import json, os, sys
import numpy as np, cv2
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
S = 2808 / 1280.0
anc = json.load(open(f'{ROOT}/layout/v001/anchor.json'))['frames']
rows = []
for i in range(52):
    al = cv2.imread(f'{ROOT}/comp/v002/work/cg_d/cg.{i:04d}.png', -1)[..., 3] / 65535.0
    c = anc[i]['corners']; out = [i]
    for key, side in (('front_left', -1), ('front_right', 1)):
        X, Y = c[key][0] * S, c[key][1] * S
        # bottom edge: in columns 12-30 px inside the corner, the lowest row where alpha crosses 0.5 (sub-px)
        cols = range(int(X) - side * 30, int(X) - side * 12) if side < 0 else range(int(X) - 30, int(X) - 12)
        cols = range(int(X) + 12, int(X) + 30) if side < 0 else range(int(X) - 30, int(X) - 12)
        ys = []
        for x in cols:
            col = al[int(Y) - 40:int(Y) + 40, x]; idx = np.where(col >= 0.5)[0]
            if len(idx) == 0: continue
            k = idx[-1]
            if k + 1 < len(col):
                a0, a1 = col[k], col[k + 1]; ys.append(int(Y) - 40 + k + (a0 - 0.5) / max(a0 - a1, 1e-6) + 0.5)
        yb = np.median(ys) if ys else np.nan
        # outer x: on rows 6-14 px above the bottom edge, where alpha crosses 0.5 going outward
        xs = []
        for y in range(int(Y) - 14, int(Y) - 6):
            r = al[y, int(X) - 60:int(X) + 60]; idx = np.where(r >= 0.5)[0]
            if len(idx) == 0: continue
            if side < 0:
                k = idx[0]
                if k > 0: a0, a1 = r[k - 1], r[k]; xs.append(int(X) - 60 + k - (a1 - 0.5) / max(a1 - a0, 1e-6) + 0.5)
            else:
                k = idx[-1]
                if k + 1 < len(r): a0, a1 = r[k], r[k + 1]; xs.append(int(X) - 60 + k + (a0 - 0.5) / max(a0 - a1, 1e-6) + 0.5)
        xo = np.median(xs) if xs else np.nan
        out += [xo / S - c[key][0], yb / S - c[key][1]]
    rows.append(out)
R = np.array(rows)
land = R[4:44]
med = np.nanmedian(land[:, 1:], axis=0)
print('frame  FLdx  FLdy  FRdx  FRdy   (plate px, residual minus median; median offsets %s)' % np.round(med, 2))
worst = 0
for r in R:
    d = r[1:] - med; tag = ''
    if 4 <= r[0] <= 43:
        worst = max(worst, np.nanmax(np.abs(d)))
    elif r[0] < 4: tag = ' (falling)'
    else: tag = ' (end whip, not gated)'
    print('s%02d  %s%s' % (r[0], '  '.join('%+5.2f' % v for v in d), tag))
print('MAX |slide| s4-s43 = %.2f plate px  -> %s' % (worst, 'PASS' if worst <= 1.0 else 'CHECK'))
