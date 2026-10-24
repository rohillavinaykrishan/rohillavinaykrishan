import numpy as np, cv2, sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
Y1 = 972  # header line starts at y~985
reg = a[:Y1].copy()
R, G = reg[..., 0], reg[..., 1]
def ss(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
al = np.maximum(ss(G, 4, 42), ss(R, 135, 205))
# remove tiny specks (grunge noise that passes key): keep components connected to big blobs
m = (al > 0.02).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] > 400
al = al * keep[lab]
# 1px feather
al = cv2.GaussianBlur(al, (0, 0), 0.7)
# background estimate (normalized conv over pure-bg pixels)
bgm = (al < 0.01).astype(np.float32)
k = (0, 0)
num = cv2.GaussianBlur(reg * bgm[..., None], k, 25); den = cv2.GaussianBlur(bgm, k, 25)[..., None]
bg = num / np.maximum(den, 1e-3)
# unpremultiply against bg -> decontaminated foreground
fg = (reg - (1 - al[..., None]) * bg) / np.maximum(al[..., None], 1e-3)
fg = np.clip(fg, 0, 255)
# for soft edges, pull colour from solid interior (push-pull) to kill red fringe noise
solid = (al > 0.9).astype(np.float32)
num = cv2.GaussianBlur(reg * solid[..., None], k, 4); den = cv2.GaussianBlur(solid, k, 4)[..., None]
inner = num / np.maximum(den, 1e-4)
w = ss(al, 0.3, 0.9)[..., None]
inner_ok = (den > 1e-3)
col = np.where(inner_ok, w * fg + (1 - w) * inner, fg)
ys, xs = np.where(al > 0.01)
pad = 24
x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, a.shape[1])
y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, Y1)
print('bbox', x0, y0, x1, y1)
rgba = np.dstack([col, al[..., None] * 255])[y0:y1, x0:x1]
rgba[al[y0:y1, x0:x1] == 0, :3] = 0
Image.fromarray(np.clip(rgba + 0.5, 0, 255).astype(np.uint8), 'RGBA').save(out, optimize=True)
