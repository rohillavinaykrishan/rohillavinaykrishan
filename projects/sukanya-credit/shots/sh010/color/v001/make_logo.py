# sf_logo_silver.png: silver/chrome SF logo, 2160 px wide, clean straight alpha.
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
src, out = sys.argv[1], sys.argv[2]
W = 2160
im = Image.open(src).convert("RGBA"); w0, h0 = im.size; H = round(h0 * W / w0)
a0 = np.asarray(im).astype(np.float32) / 255
pre = a0[..., :3] * a0[..., 3:4]
def up(x): return np.asarray(Image.fromarray(x.astype(np.float32), "F").resize((W, H), Image.LANCZOS))
A = np.clip(up(a0[..., 3]), 0, 1)
P = np.stack([np.clip(up(pre[..., c]), 0, 1) for c in range(3)], -1)
# alpha cleanup: kill haze, drop specks/islands not connected to letters
A[A < 0.03] = 0
lab, n = nd.label(A > 0.12)
sizes = nd.sum(np.ones_like(A), lab, range(1, n + 1))
keep = np.zeros(n + 1, bool); keep[1:] = sizes >= 400
grow = nd.binary_dilation(keep[lab], iterations=3)
A = A * grow
rgb = np.where(A[..., None] > 1e-3, P / np.maximum(A[..., None], 1e-3), 0).clip(0, 1)
L = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
# texture = luma high-pass (alpha-weighted blur) -> keeps the brush grit, drops the yellow->red gradient
def wblur(x, s):
    return nd.gaussian_filter(x * A, s) / np.maximum(nd.gaussian_filter(A, s), 1e-4)
detail = np.clip(L - wblur(L, 10), -0.25, 0.25)
# bevel from alpha distance, lit from upper-left
inside = A > 0.5
d = nd.distance_transform_edt(inside)
hgt = nd.gaussian_filter(np.clip(d / 10.0, 0, 1) ** 0.7, 1.5)
gy, gx = np.gradient(hgt)
nx, ny, nz = -gx * 6, -gy * 6, np.ones_like(gx)
nrm = np.sqrt(nx**2 + ny**2 + nz**2); nx, ny, nz = nx/nrm, ny/nrm, nz/nrm
lx, ly, lz = -0.55, -0.65, 0.52; ln = (lx*lx+ly*ly+lz*lz) ** .5
diff = (nx*lx + ny*ly + nz*lz) / ln
spec = np.clip(diff, 0, 1) ** 24
# chrome body: bright top, a darker horizon band below the middle of each region, lift at the bottom
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
yn = yy / H; xn = xx / W
diag = (yn * 0.8 + (1 - xn) * 0.2)
# two chrome bands, one per text line (STREET upper, FIGHTER lower): bright sky above a dark horizon in each
row = np.where(yn + 0.25 * xn < 0.62, (yn + 0.25 * xn) / 0.62, (yn + 0.25 * xn - 0.62) / 0.63)
prof_x = [0.00, 0.30, 0.52, 0.58, 0.64, 0.80, 1.00]
prof_y = [0.93, 0.86, 0.66, 0.40, 0.58, 0.80, 0.93]   # continuous chrome profile, f(0) = f(1): no seam between the rows
body = nd.gaussian_filter(np.interp(row, prof_x, prof_y), 3)
t = body + 1.3 * detail + 0.45 * (diff - 0.75) + 0.6 * spec
t = t - 0.18 * (1 - hgt)                 # slight dark rim at the edge = metal edge
t = np.clip(t, 0, 1)
lo = np.array([0x1A, 0x1A, 0x1C]) / 255.0; hi = np.array([0xF4, 0xEF, 0xE6]) / 255.0
col = lo + t[..., None] * (hi - lo)
o = np.dstack([col, A]); o = (o * 255 + 0.5).clip(0, 255).astype(np.uint8)
o[A <= 0] = 0                              # clean zero-alpha pixels
Image.fromarray(o, "RGBA").save(out, optimize=True)
print(out, o.shape, "alpha>0 px", int((A > 0).sum()), "islands kept", int(keep.sum()), "of", n)
