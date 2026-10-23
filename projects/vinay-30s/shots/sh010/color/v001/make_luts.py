#!/usr/bin/env python3
"""Build the SPECTRUM LUTs (treatment section 5): 8 DUO, TRUE, DRAIN. 33^3 .cube, sRGB/Rec.709 code values in/out."""
import json, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CUES = os.path.join(HERE, "../../director/v001/cues.json")
N = 33
pal = json.load(open(CUES))["palette"]
INK = pal["Ink"]; WH = pal["White Hot"]
SLUG = {"Ryu": "ryu", "Ken": "ken", "Dhalsim": "dhalsim", "Blanka": "blanka", "Guile": "guile",
        "Chun-Li": "chunli", "M. Bison": "bison", "E. Honda": "honda"}

def hex2rgb(h): h = h.lstrip("#"); return np.array([int(h[i:i+2], 16) / 255 for i in (0, 2, 4)])
def s2l(c): c = np.asarray(c, float); return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def l2s(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
def lin2lab(rgb): return np.cbrt(rgb @ M1.T) @ M2.T
def lab2lin(lab): return (lab @ np.linalg.inv(M2).T) ** 3 @ np.linalg.inv(M1).T
def s2lab(c): return lin2lab(s2l(c))
def lab2s(lab): return l2s(lab2lin(lab))

def in_gamut(lab, eps=1e-4):
    l = lab2lin(lab); return np.all((l >= -eps) & (l <= 1 + eps), axis=-1)

def gamut_map(lab):
    """Reduce OKLab chroma (keep L, hue) until inside sRGB. Vectorised bisection."""
    lab = np.array(lab, float); shp = lab.shape; lab = lab.reshape(-1, 3)
    ok = in_gamut(lab); lo = np.zeros(len(lab)); hi = np.ones(len(lab))
    for _ in range(24):
        mid = (lo + hi) / 2; t = lab.copy(); t[:, 1:] *= mid[:, None]
        g = in_gamut(t); lo = np.where(g, mid, lo); hi = np.where(g, hi, mid)
    out = lab.copy(); out[~ok, 1:] *= lo[~ok, None]
    return out.reshape(shp)

def grid():
    v = np.linspace(0, 1, N)
    b, g, r = np.meshgrid(v, v, v, indexing="ij")          # .cube order: R fastest
    return np.stack([r, g, b], -1).reshape(-1, 3)

def write_cube(path, title, rgb):
    rgb = np.clip(rgb, 0, 1)
    with open(path, "w") as f:
        f.write(f'TITLE "{title}"\nLUT_3D_SIZE {N}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        for p in rgb: f.write(f"{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n")

def pchip(xs, ys, x):
    """Monotone cubic (Fritsch-Carlson) - the shape ffmpeg 'curves' uses closely enough."""
    xs, ys = np.array(xs, float), np.array(ys, float); h = np.diff(xs); d = np.diff(ys) / h
    m = np.zeros_like(xs); m[1:-1] = np.where(d[:-1] * d[1:] > 0, 2 / (1 / d[:-1] + 1 / d[1:]), 0); m[0], m[-1] = d[0], d[-1]
    i = np.clip(np.searchsorted(xs, x) - 1, 0, len(h) - 1); t = (x - xs[i]) / h[i]
    h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t; h01 = -2*t**3 + 3*t**2; h11 = t**3 - t**2
    return h00*ys[i] + h10*h[i]*m[i] + h01*ys[i+1] + h11*h[i]*m[i+1]

# ---------- DUO: luma -> OKLab gradient map ----------
PRE = ([0, .1, .5, .9, 1], [0, .04, .48, .92, 1])
def duo_stops(hexc):
    hue = s2lab(hex2rgb(hexc)); ink = s2lab(hex2rgb(INK)); wh = s2lab(hex2rgb(WH))
    dark = hue.copy(); C = np.hypot(hue[1], hue[2]); dark[0] = 0.30   # OKLCH L 0.30, same hue
    dark = gamut_map(dark)
    hi = gamut_map(0.55 * hue + 0.45 * wh)                              # hue mixed 45% with White Hot (OKLab)
    return [0, .28, .60, .86, 1.0], np.array([ink, dark, hue, hi, wh])

def duo(rgb, hexc):
    c = pchip(*PRE, rgb)
    y = np.clip(c @ np.array([0.2126, 0.7152, 0.0722]), 0, 1)          # Rec.709 luma on code values
    xs, labs = duo_stops(hexc)
    lab = np.stack([np.interp(y, xs, labs[:, k]) for k in range(3)], -1)
    return lab2s(gamut_map(lab))

# ---------- TRUE ----------
def hue_w(h, centre, width):
    d = np.angle(np.exp(1j * (h - np.deg2rad(centre))));  return np.clip(np.cos(np.clip(d / np.deg2rad(width), -1, 1) * np.pi / 2), 0, 1) ** 2

def true_grade(rgb, chroma_k=1.0, ev=0.0):
    lin = s2l(rgb)
    lin = lin * np.array([1.025, 1.0, 0.955])                            # warm white balance (R >= B bias)
    lin = lin * 2 ** ev
    lab = lin2lab(np.clip(lin, 0, None))
    L, a, b = lab[:, 0], lab[:, 1], lab[:, 2]
    C = np.hypot(a, b); h = np.arctan2(b, a)                             # OKLCH hue (rad)
    warm = np.maximum(hue_w(h, 50, 75), hue_w(h, 140, 40))               # reds/skin/oranges/yellows (~-25..125), greens (~100..180)
    blue = hue_w(h, 255, 45)                                             # blues 210..300
    C = C * (1 + 0.12 * warm) * (1 - 0.15 * blue)
    h = h + np.deg2rad(10) * blue                                        # pull blues 10 deg towards violet
    # S-curve on L: contrast around 0.5 with a toe and shoulder
    x = np.clip(L, 0, 1)
    s = np.where(x < 0.5, 0.5 * (2 * x) ** 1.35, 1 - 0.5 * (2 * (1 - x)) ** 1.35)
    L2 = 0.75 * s + 0.25 * x
    C = C * np.where(L > 1e-4, np.minimum(L2 / np.maximum(L, 1e-4), 1.25), 0) ** 0.5   # keep chroma with lightness
    C = C * chroma_k
    lab = np.stack([L2, C * np.cos(h), C * np.sin(h)], -1)
    out = lab2s(gamut_map(lab))
    ink = hex2rgb(INK); top = hex2rgb(WH) * 0.985                        # shadows to Ink, highlights roll to White Hot (no 255)
    return ink + (top - ink) * out

if __name__ == "__main__":
    g = grid()
    for name, hx in pal["fighters"].items():
        write_cube(os.path.join(HERE, f"duo_{SLUG[name]}.cube"), f"DUO {name} {hx}", duo(g, hx))
        xs, labs = duo_stops(hx)
        print(f"duo_{SLUG[name]}.cube", hx, "stops:", " ".join("#%02X%02X%02X" % tuple(np.round(lab2s(l) * 255).astype(int)) for l in labs))
    write_cube(os.path.join(HERE, "true.cube"), "TRUE", true_grade(g))
    write_cube(os.path.join(HERE, "drain.cube"), "DRAIN (TRUE @15% chroma, -0.3EV)", true_grade(g, chroma_k=0.15, ev=-0.3))
    print("true.cube drain.cube")
