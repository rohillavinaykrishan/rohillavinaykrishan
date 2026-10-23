#!/usr/bin/env python3
"""Build the SUPER ART LUTs (treatment section 5). Colorist, sh010 color v001.
All maths in float: sRGB(Rec.709 video, display-referred) <-> linear <-> OKLab.
Outputs (65^3 .cube, input/output in full-range R'G'B' 0-1):
  tritone.cube  Act 1-2 panels, echo bands, title line-up
  drain.cube    C00 charge (f243-260): tritone at 35% chroma, -0.3 EV
  band.cube     Act 3 band B01-B08: designed full colour, blues -> violet-mulberry
  title_lineup.cube  tritone tuned for the line-up art (slightly brighter mids)
  logo_gold.cube     SF logo luma -> burnt saffron -> Saffron -> Ki White
Usage: python3 make_luts.py [outdir]   (also importable: tritone(), band(), ...)"""
import sys, os
import numpy as np

PAL = dict(aub="#14080F", mul="#4A1838", plum="#7A2E5C", saf="#FFB12A",
           ki="#FFF3DC", chalk="#D9CFC3", cin="#FF5A1F")

def hex2rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) / 255 for i in (0, 2, 4)])

def s2l(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)

def l2s(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)

M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
               [0.2119034982, 0.6806995451, 0.1073969566],
               [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
               [1.9779984951, -2.4285922050, 0.4505937099],
               [0.0259040371, 0.7827717662, -0.8086757660]])
M1i, M2i = np.linalg.inv(M1), np.linalg.inv(M2)

def srgb2oklab(rgb):
    lms = s2l(rgb) @ M1.T
    return np.cbrt(lms) @ M2.T

def oklab2srgb(lab):
    lms = (lab @ M2i.T) ** 3
    lin = lms @ M1i.T
    return l2s(gamut_fit(lin))

def gamut_fit(lin):
    """Soft gamut fit in linear: pull out-of-gamut colours toward their own luminance."""
    Y = (lin @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    Y = np.clip(Y, 0, 1)
    d = lin - Y
    # max t in [0,1] so Y + t*d stays inside [0,1]
    with np.errstate(divide='ignore', invalid='ignore'):
        tl = np.where(d < 0, Y / -d, np.inf)
        th = np.where(d > 0, (1 - Y) / d, np.inf)
    t = np.clip(np.min(np.minimum(tl, th), axis=-1, keepdims=True), 0, 1)
    return Y + d * t

def luma709(rgb):
    return rgb @ np.array([0.2126, 0.7152, 0.0722])

def curve(x, pts):
    xs, ys = zip(*pts)
    # monotone cubic (PCHIP-like) through the points, like ffmpeg curves
    from numpy import interp
    xs = np.array(xs); ys = np.array(ys)
    h = np.diff(xs); dlt = np.diff(ys) / h
    m = np.zeros_like(ys)
    m[1:-1] = np.where(dlt[:-1] * dlt[1:] > 0, 2 / (1 / dlt[:-1] + 1 / dlt[1:]), 0)
    m[0], m[-1] = dlt[0], dlt[-1]
    x = np.clip(x, xs[0], xs[-1])
    i = np.clip(np.searchsorted(xs, x) - 1, 0, len(h) - 1)
    t = (x - xs[i]) / h[i]
    h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t; h01 = -2*t**3 + 3*t**2; h11 = t**3 - t**2
    return h00*ys[i] + h10*h[i]*m[i] + h01*ys[i+1] + h11*h[i]*m[i+1]

TRI_STOPS = [(0.0, PAL['aub']), (0.25, PAL['mul']), (0.5, PAL['plum']), (0.78, PAL['saf']), (1.0, PAL['ki'])]
TRI_LAB = np.array([srgb2oklab(hex2rgb(h)) for _, h in TRI_STOPS])
TRI_POS = np.array([p for p, _ in TRI_STOPS])

def ramp_lab(t, stops_pos=TRI_POS, stops_lab=TRI_LAB):
    t = np.clip(t, 0, 1)
    return np.stack([np.interp(t, stops_pos, stops_lab[:, k]) for k in range(3)], -1)

def tritone(rgb, ev=0.0, chroma=1.0, crv=((0, 0), (0.12, 0.06), (0.5, 0.45), (0.85, 0.85), (1, 1))):
    y = luma709(rgb)                      # Rec.709 weights on the R'G'B' signal (as SVG/ffmpeg do)
    if ev:
        y = l2s(s2l(y) * 2 ** ev)         # exposure in linear light, before the map: floor stays Aubergine
    y = curve(y, crv)
    lab = ramp_lab(y)
    if chroma != 1.0:
        lab[..., 1:] *= chroma
    return oklab2srgb(lab)

def drain(rgb):
    return tritone(rgb, ev=-0.3, chroma=0.35)

def title_lineup(rgb):
    return tritone(rgb, crv=((0, 0), (0.12, 0.07), (0.5, 0.50), (0.85, 0.88), (1, 1)))

def logo_gold(rgb):
    y = luma709(rgb)
    saf = srgb2oklab(hex2rgb(PAL['saf'])); ki = srgb2oklab(hex2rgb(PAL['ki']))
    burnt = saf.copy(); burnt[0] *= 0.62; burnt[1:] *= 0.85   # burnt saffron (#9C5A0E-ish) for depth
    pos = np.array([0.0, 0.55, 1.0]); labs = np.stack([burnt, saf, ki])
    return oklab2srgb(ramp_lab(curve(y, ((0, 0), (0.5, 0.5), (0.8, 0.86), (1, 1))), pos, labs))

def smooth_bump(h, centre, half):
    d = np.abs((h - centre + 180) % 360 - 180)
    return np.where(d < half, 0.5 + 0.5 * np.cos(np.pi * d / half), 0.0)

def balance_lab(lab, cast=(0.0, 0.0), k=1.0, warm=0.012):
    """Per-shot primary balance in OKLab: remove k x the shot's mean (a,b) cast vector and add a
    small warm offset toward Saffron's hue (75 deg). A shift in (a,b) moves blue toward neutral
    instead of toward cyan/green (which RGB channel gains do)."""
    L = lab[..., 0]
    w = np.clip(L / 0.45, 0, 1) ** 0.8               # blacks get less shift (toe goes to Aubergine anyway)
    hs = np.radians(75)
    da = -k * min(cast[0], 0.0) + warm * np.cos(hs)   # only remove a green cast; never push magenta to green
    db = -k * cast[1] + warm * np.sin(hs)
    out = lab.copy()
    out[..., 1] += da * w; out[..., 2] += db * w
    return out

def shot_cast(rgb_frames):
    """Mean OKLab (a,b) of a shot, weighted to midtones/highlights (what the eye reads as the cast)."""
    acc = np.zeros(2); wsum = 0.0
    for f in rgb_frames:
        lab = srgb2oklab(f.reshape(-1, 3))
        w = np.clip((lab[:, 0] - 0.2) / 0.3, 0, 1)
        acc += (lab[:, 1:] * w[:, None]).sum(0); wsum += w.sum()
    return acc / max(wsum, 1e-6)

def band(rgb, cast=(0.0, 0.0), k=0.0, warm=0.0):
    """UNLOCK grade. band.cube = no per-shot trim; band_<ID>.cube = balance_lab(cast) then this."""
    lab = srgb2oklab(rgb)
    if k or warm:
        lab = balance_lab(lab, cast, k, warm)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, b); h = np.degrees(np.arctan2(b, a)) % 360
    # 1. blues -> violet-mulberry. Treatment: hue +35, chroma x0.7. A plain +35 leaves pure blue
    #    (h~265) at violet h~300 where B > R, so the warp is monotonic piecewise: +35 at the
    #    cyan edge rising to +56 on blue, landing on 321-340 (R ~= B .. mulberry 344).
    HK = [150, 195, 235, 265, 290, 325, 355]
    HV = [150, 207, 290, 321, 333, 342, 355]
    hw = np.where((h > 150) & (h < 355), np.interp(h, HK, HV), h)
    wb = smooth_bump(h, 250, 80)                       # blue weight 170..330, peak on blue
    h = hw
    C = C * (1 - 0.3 * wb)
    # 2. no green: greens/olives/teals (h 95-200) are pulled toward ochre-saffron and lose chroma,
    #    hardest in the shadows and mids (the board mock's B01 went green there)
    wg = smooth_bump(h, 150, 60)
    wl = np.clip(1 - (L - 0.35) / 0.45, 0.35, 1)
    dh = ((85 - h + 180) % 360) - 180
    h = h + dh * 0.6 * wg * wl
    C = C * (1 - 0.6 * wg * wl)
    # 3. saturation 1.15 on skin / reds / oranges / greens (h ~ 0-150)
    ws = smooth_bump(h, 75, 85) * (1 - wb)
    C = C * (1 + 0.15 * ws)
    # 4. contrast S-curve on L (pivot ~0.5)
    L = curve(L, ((0, 0), (0.22, 0.13), (0.5, 0.48), (0.78, 0.84), (1, 1)))
    # 5. shadows sit on Aubergine: black floor + warm tint in the toe
    aub = srgb2oklab(hex2rgb(PAL['aub'])); ki = srgb2oklab(hex2rgb(PAL['ki']))
    L = aub[0] + (ki[0] - aub[0]) * L                  # floor at Aubergine, ceiling at Ki White
    ar, br = C * np.cos(np.radians(h)), C * np.sin(np.radians(h))
    ws_ = np.clip(1 - (L - aub[0]) / 0.30, 0, 1) ** 1.5
    ar = ar * (1 - ws_) + aub[1] * ws_
    br = br * (1 - ws_) + aub[2] * ws_
    # 6. highlights roll off to Ki White
    wh = np.clip((L - 0.80) / (ki[0] - 0.80), 0, 1) ** 1.5
    ar = ar * (1 - wh) + ki[1] * wh
    br = br * (1 - wh) + ki[2] * wh
    return oklab2srgb(np.stack([L, ar, br], -1))

def write_cube(path, fn, n=65, title=None):
    g = np.linspace(0, 1, n)
    # .cube order: R fastest, then G, then B
    B, G, R = np.meshgrid(g, g, g, indexing='ij')
    rgb = np.stack([R, G, B], -1).reshape(-1, 3)
    out = np.clip(fn(rgb), 0, 1)
    with open(path, 'w') as f:
        f.write(f'TITLE "{title or os.path.basename(path)}"\n# sukanya-v2 sh010 colorist v001 - make_luts.py\n')
        f.write(f'LUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        np.savetxt(f, out, fmt='%.6f')

if __name__ == '__main__':
    od = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    for name, fn in [('tritone', tritone), ('drain', drain), ('band', band),
                     ('title_lineup', title_lineup), ('logo_gold', logo_gold)]:
        write_cube(os.path.join(od, name + '.cube'), fn); print('wrote', name)
