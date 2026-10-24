import sys, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
W = np.array([0.2126, 0.7152, 0.0722])
bad = 0; rows = []
for i in range(52):
    a = np.asarray(Image.open(f"{src}/plate.{i:04d}.png").convert("RGB")).astype(float)
    b = np.asarray(Image.open(f"{dst}/plate.{i:04d}.png").convert("RGB")).astype(float)
    ya, yb = (a @ W).mean(), (b @ W).mean()
    m = b.reshape(-1, 3).mean(0); sky = b[:60].reshape(-1, 3).mean(0)
    # VAVG (Cr) in BT.601 limited
    cr = (128 + (0.439*b[...,0] - 0.368*b[...,1] - 0.071*b[...,2]) * 219/255).mean()
    ok = m[2] <= m[1] <= m[0] and sky[2] <= sky[1] <= sky[0] and cr >= 128 and 0.03 <= yb/ya-1 <= 0.08
    bad += not ok
    rows.append((i, yb/ya-1, m, sky, cr, ok))
for r in rows:
    if r[0] in (0, 12, 25, 38, 51) or not r[5]:
        print(f"s{r[0]:02d} dY {r[1]*100:+.1f}%  RGB {r[2].round(1)}  sky {r[3].round(1)}  Cr {r[4]:.1f}  {'OK' if r[5] else 'FAIL'}")
d = [r[1] for r in rows]
print("dY range %.1f%% .. %.1f%%, fails %d/52" % (min(d)*100, max(d)*100, bad))
