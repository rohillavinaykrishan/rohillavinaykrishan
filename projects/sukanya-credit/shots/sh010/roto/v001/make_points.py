"""Build points.json (hero point cloud) + review/points_preview.png.

usage: vfx-python make_points.py [N_EDGE] [N_RAND] [DOT_PX_4K]
Schema: {"w":2160,"h":3840,"f":2600,"cx":1080,"cy":1920,"z_near":..,"z_far":..,
         "points":[[x,y,z,l],...]}
  x,y : pixel position in the 2160x3840 frame (the solved pose reprojects here)
  z   : camera-space depth Zc at the solved pose (camera at world z=2600, f=2600);
        smaller = nearer. Range z_near..z_far (behind the names, which sit at Zc 2600).
  l   : luminance 0..1 (draw alpha = l*0.8 per treatment section 7)
Unproject: Xw=(x-1080)*z/2600, Yw=(y-1920)*z/2600, Zw=2600-z.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
N_EDGE = int(sys.argv[1]) if len(sys.argv) > 1 else 2700
N_RAND = int(sys.argv[2]) if len(sys.argv) > 2 else 700
DOT = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
Z_NEAR, Z_FAR, F = 2700.0, 5200.0, 2600.0
rng = np.random.default_rng(271)

rgb = np.asarray(Image.open(os.path.join(HERE, "hero_1080.png")).convert("RGB")).astype(np.float32) / 255
# B&W world: Rec.709 luma, then a gentle contrast lift so skin vs shadow separates
# The plate is lit almost entirely in blue and the background (0,45,100) is nearly as bright
# as her skin (53,77,115) in blue/Rec.709. The red/green channels separate skin from the blue
# wall, so use a red-weighted B&W mix (a red-filter silver print), then CLAHE for local relief.
import cv2
mix = rgb @ np.array([0.55, 0.35, 0.10], np.float32)
lo, hi = np.percentile(mix, [2, 99.7])
mix = np.clip((mix - lo) / (hi - lo), 0, 1)
clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(6, 10))
luma = clahe.apply((mix * 255).astype(np.uint8)).astype(np.float32) / 255
luma = np.clip(luma, 0, 1) ** 0.9
dep = np.asarray(Image.open(os.path.join(HERE, "hero_depth.png"))).astype(np.float32)
dep = dep / dep.max()  # 1 = near
H, W = luma.shape
# subject weight from depth (she is the near layer): background points cost the face density
subj = np.clip((dep - 0.30) / 0.25, 0, 1)
subj = subj * subj * (3 - 2 * subj)
# hand-placed face prior (roto ellipse, 1080 coords): centre (680,690), radii (400,440), soft edge.
# 3,400 dots cannot cover the whole frame densely; the face gets most of them.
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt(((xx - 680) / 400) ** 2 + ((yy - 690) / 440) ** 2)
face = np.clip((1.25 - rr) / 0.35, 0, 1)
subj = subj * (0.18 + 0.82 * face)

# Sobel on a lightly blurred luma (kills compression noise)
lb = np.asarray(Image.fromarray((luma * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255
p = np.pad(lb, 1, mode="edge")
gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
g = np.hypot(gx, gy)
# edges that are invisible (both sides dark) are useless as dots: weight by local brightness
g_vis = g * (0.25 + 0.75 * lb) * (0.12 + 0.88 * subj)
thr = np.percentile(g_vis, 90)  # top 10 % (6 % starved the soft facial features)
mask = g_vis >= thr
idx = np.flatnonzero(mask)
w = np.sqrt(g_vis.ravel()[idx])  # flatter than linear: hair/collar edges must not eat the eyes
e_sel = rng.choice(idx, size=min(N_EDGE, idx.size), replace=False, p=w / w.sum())
# fill points: luma-weighted (dark pixels would be invisible anyway), not on edges
rest = np.flatnonzero(~mask)
wr = (luma.ravel()[rest] ** 1.5) * (0.08 + 0.92 * subj.ravel()[rest]) + 1e-5
r_sel = rng.choice(rest, size=N_RAND, replace=False, p=wr / wr.sum())
sel = np.concatenate([e_sel, r_sel])

v, u = np.divmod(sel, W)
ju, jv = rng.uniform(-0.5, 0.5, (2, sel.size))
x = (u + 0.5 + ju) * 2.0
y = (v + 0.5 + jv) * 2.0
d = dep.ravel()[sel]
z = Z_NEAR + (1.0 - d) * (Z_FAR - Z_NEAR)
l = np.clip(0.25 + 0.75 * luma.ravel()[sel], 0, 1) ** 0.7  # display luma: floor + lift so alpha=l*0.8 stays visible
pts = [[round(float(a), 1), round(float(b), 1), round(float(c), 1), round(float(e), 3)]
       for a, b, c, e in zip(x, y, z, l)]
out = {"w": 2160, "h": 3840, "f": F, "cx": 1080, "cy": 1920, "z_near": Z_NEAR, "z_far": Z_FAR,
       "n_edge": int(e_sel.size), "n_fill": int(r_sel.size), "src": "trailer 151.90 s, CX 770",
       "points": pts}
with open(os.path.join(HERE, "points.json"), "w") as fh:
    json.dump(out, fh, separators=(",", ":"))

# ---------- preview: frontal (solved pose) | yaw 25 deg orbit, drawn at 1080x1920 ----------
P = np.array(pts, np.float32)
Xw = (P[:, 0] - 1080) * P[:, 2] / F
Yw = (P[:, 1] - 1920) * P[:, 2] / F
Zw = 2600 - P[:, 2]


def render(yaw_deg):
    img = Image.new("RGB", (1080, 1920), (7, 7, 7))
    dr = ImageDraw.Draw(img)
    a = np.radians(yaw_deg)
    piv = -600.0  # orbit around the face depth (Zc ~3200)
    xr = Xw * np.cos(a) + (Zw - piv) * np.sin(a)
    zr = -Xw * np.sin(a) + (Zw - piv) * np.cos(a) + piv
    zc = 2600 - zr
    sx = (1080 + F * xr / zc) / 2
    sy = (1920 + F * Yw / zc) / 2
    r = DOT / 4  # 4K dot diameter -> radius at half res
    for i in np.argsort(-zc):
        c = int(round(217 * P[i, 3] * 0.8 + 7 * (1 - P[i, 3] * 0.8)))
        dr.ellipse([sx[i] - r, sy[i] - r, sx[i] + r, sy[i] + r], fill=(c, c - 2, c - 7))
    return img


os.makedirs(os.path.join(HERE, "review"), exist_ok=True)
sheet = Image.new("RGB", (2160, 1920))
sheet.paste(render(0), (0, 0))
sheet.paste(render(25), (1080, 0))
sheet.save(os.path.join(HERE, "review", "points_preview.png"))
print(f"points {len(pts)} (edge {e_sel.size}, fill {r_sel.size}), z {P[:,2].min():.0f}-{P[:,2].max():.0f}")
