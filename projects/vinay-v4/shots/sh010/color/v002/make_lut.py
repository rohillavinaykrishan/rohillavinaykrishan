#!/usr/bin/env python3
"""sh010 colour v002 (director note 13): build sunbleach.cube (SUN-BLEACHED, treatment section 5).

Display-referred (Rec.709/sRGB code values in, code values out).
Order: midtone lift -> creamy shoulder -> sat 0.88 + greens to sage/olive
       -> per-channel map black->Ink #12100D, white->Bone #F2EBDF.
usage: python3 make_lut.py out.cube [size]
"""
import sys
import numpy as np

INK = np.array([0x12, 0x10, 0x0D]) / 255.0
BONE = np.array([0xF2, 0xEB, 0xDF]) / 255.0

GAMMA = float(__import__("os").environ.get("SB_GAMMA", "0.98"))       # midtone lift; compensates the Ink/Bone squeeze (keeps mean Y within +-5%)
SHOULDER = 0.72     # highlight roll-off starts here
SAT = 1.00
GREEN_SAT = 0.85    # extra desat for foliage
SKIN_SAT = 1.08    # skin + red suit
MID = float(__import__("os").environ.get("SB_MID", "0.50"))  # output of 0.5 in the contrast curve
SAGE_HUE = 72.0     # deg, sage #7D875C is ~74 deg
GREEN_SHIFT = 0.50  # fraction of the way toward SAGE_HUE


def rgb2hsv(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx = c.max(-1); mn = c.min(-1); d = mx - mn
    h = np.zeros_like(mx)
    nz = d > 1e-9
    i = nz & (mx == r); h[i] = ((g - b)[i] / d[i]) % 6
    i = nz & (mx == g) & (mx != r); h[i] = (b - r)[i] / d[i] + 2
    i = nz & (mx == b) & (mx != r) & (mx != g); h[i] = (r - g)[i] / d[i] + 4
    s = np.where(mx > 1e-9, d / np.maximum(mx, 1e-9), 0)
    return np.stack([h * 60.0, s, mx], -1)


def hsv2rgb(c):
    h, s, v = c[..., 0] / 60.0 % 6, c[..., 1], c[..., 2]
    i = np.floor(h).astype(int); f = h - i
    p = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    out = np.zeros(c.shape)
    sel = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    for k, (a, b, cc) in enumerate(sel):
        m = i == k
        out[..., 0][m] = a[m]; out[..., 1][m] = b[m]; out[..., 2][m] = cc[m]
    return out


def shoulder(x):
    k = SHOULDER; w = 1 - k
    y = x.copy()
    m = x > k
    t = (x[m] - k) / w
    y[m] = k + w * (np.tanh(1.3 * t) / np.tanh(1.3))  # 1 -> 1, softer approach
    return y


def hermite(x, pts):
    """piecewise cubic Hermite through (x, y, slope) knots"""
    y = np.zeros_like(x)
    for (x0, y0, m0), (x1, y1, m1) in zip(pts[:-1], pts[1:]):
        sel = (x >= x0) & (x <= x1)
        h = x1 - x0; t = (x[sel] - x0) / h
        h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t; h01 = -2*t**3 + 3*t**2; h11 = t**3 - t**2
        y[sel] = h00*y0 + h10*h*m0 + h01*y1 + h11*h*m1
    return y


def contrast(x):
    # toe: 10% grey -> 7% (black stays 0 -> Ink after the map); mid-slope 1.08; top left to shoulder()
    return np.clip(hermite(x, [(0, 0, 0.55), (0.10, 0.07, 0.85), (0.50, MID, 1.08), (1.0, 1.0, 0.90)]), 0, 1)


def grade(rgb):
    x = np.clip(rgb, 0, 1) ** GAMMA
    x = contrast(x)
    x = shoulder(x)
    hsv = rgb2hsv(x)
    h = hsv[..., 0]
    # green weight: smooth bump over 70-170 deg (foliage), zero on skin/red/orange (<45)
    g = np.clip((h - 50) / 30, 0, 1) * np.clip((185 - h) / 30, 0, 1)
    hsv[..., 0] = h + (SAGE_HUE - h) * GREEN_SHIFT * g * (h > SAGE_HUE)
    # skin / red suit weight: full 335-25 deg, fades out by 33 deg (sand sits at ~34-40) and 320
    hh = (h + 40) % 360  # 320 -> 0, 25 -> 65, 33 -> 73
    sk = np.clip(hh / 15, 0, 1) * np.clip((73 - hh) / 8, 0, 1)
    satk = SAT * (1 - g - sk) + GREEN_SAT * g + SKIN_SAT * sk
    hsv[..., 1] = np.clip(hsv[..., 1] * satk, 0, 1)
    x = hsv2rgb(hsv)
    return INK + x * (BONE - INK)


def main():
    out = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 33
    lin = np.linspace(0, 1, n)
    # .cube order: R fastest, then G, then B
    b, g, r = np.meshgrid(lin, lin, lin, indexing="ij")
    grid = np.stack([r, g, b], -1).reshape(-1, 3)
    res = np.clip(grade(grid), 0, 1)
    with open(out, "w") as f:
        f.write('TITLE "sh010 sunbleach v002 - Ink/Umber/Sand/Bone/Sage"\n')
        f.write(f"LUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n")
        for v in res:
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")


if __name__ == "__main__":
    main()
