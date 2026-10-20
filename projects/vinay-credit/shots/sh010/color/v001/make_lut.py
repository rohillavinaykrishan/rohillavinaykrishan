#!/usr/bin/env python3
"""Fire-lit gradient-map LUT (treatment sec.5). Usage: make_lut.py out.cube [variant]"""
import sys, numpy as np
N = 33
import os
KBASE = float(os.environ.get("KBASE", "0.66")); REDAMT = float(os.environ.get("REDAMT", "0.75"))
GAM = float(os.environ.get("GAM", "1.06"))
STOPS = [(0.00, "#050202"), (0.25, "#3A0D08"), (0.50, "#8E1A0E"),
         (0.72, "#E0581A"), (0.90, "#F5B53C"), (1.00, "#FFE7B0")]
def hx(h): return np.array([int(h[i:i+2], 16) for i in (1, 3, 5)]) / 255.0
P = np.array([s[0] for s in STOPS]); C = np.stack([hx(s[1]) for s in STOPS])

def gmap(y):
    out = np.empty(y.shape + (3,))
    for c in range(3): out[..., c] = np.interp(y, P, C[:, c])
    return out

def build(variant):
    v = np.linspace(0, 1, N)
    b, g, r = np.meshgrid(v, v, v, indexing="ij")      # r fastest when flattened
    rgb = np.stack([r, g, b], -1)
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    warm = rgb * np.array([1.05, 0.92, 0.55])
    if variant == "spec":
        out = 0.72 * gmap(Y) + 0.28 * warm
    elif variant == "v3":
        # luma weighted toward red: red costumes/skin ride up into the red-orange band,
        # blue/teal sources sink into ember shadow instead of glowing gold
        Yw = 0.40 * r + 0.55 * g + 0.05 * b
        # contrast: gamma + S-curve, deep blacks
        Yc = Yw ** GAM
        Yc = Yc + 0.35 * (Yc - 0.5) * np.sin(np.pi * Yc) * 0.6
        Yc = (Yc - 0.02).clip(0, 1) / 0.98
        # shoulder: highlights roll into gold; white (1.0) lands at 0.94 (gold to pale gold), never pure
        t0 = 0.70; top = 0.94
        Yc = np.where(Yc > t0, t0 + (top - t0) * (1 - np.exp(-(Yc - t0) / (top - t0))) / (1 - np.exp(-(1 - t0) / (top - t0))), Yc)
        gm = gmap(Yc.clip(0, 1))
        mx = rgb.max(-1); mn = rgb.min(-1); sat = (mx - mn) / np.maximum(mx, 1e-6)
        # skin: warm hue, moderate sat -> keep more original warm colour (peach, not plastic orange)
        hue_ok = (r >= g) & (g >= b)
        skin = hue_ok * np.clip((sat - 0.10) / 0.10, 0, 1) * np.clip((0.70 - sat) / 0.15, 0, 1) * np.clip((mx - 0.15) / 0.2, 0, 1)
        warm = np.stack([r * 1.02, g * 0.86, b * 0.55], -1)
        wy = 0.2126*warm[...,0] + 0.7152*warm[...,1] + 0.0722*warm[...,2]
        gy = 0.2126*gm[...,0] + 0.7152*gm[...,1] + 0.0722*gm[...,2]
        warm_m = (warm * (gy / np.maximum(wy, 1e-4))[..., None]).clip(0, 1)   # match gradient brightness
        k = KBASE - 0.25 * skin
        out = k[..., None] * gm + (1 - k[..., None]) * warm_m
        # red separation: costumes / gloves / head paint become Street Fighter red, not orange
        gr = np.maximum(g, b) / np.maximum(r, 1e-6)          # skin ~0.6-0.8, red cloth ~0.1-0.45
        ss = lambda e0, e1, v: (lambda t: t * t * (3 - 2 * t))(np.clip((v - e0) / (e1 - e0), 0, 1))
        hue = 60 * (g - b) / np.maximum(r - np.minimum(g, b), 1e-6)   # deg, valid where r is max; skin ~15-30
        redness = ss(0.55, 0.20, gr) * ss(14.0, 2.0, hue) * (r >= np.maximum(g, b)) * np.clip((r - 0.04) / 0.25, 0, 1)
        sf = np.array([0.80, 0.075, 0.07])
        lev = np.clip(r * 1.05, 0, 1) ** 1.1
        redcol = sf[None, None, None, :] * lev[..., None] / 0.80 * 0.85
        redcol = redcol + np.clip(lev - 0.85, 0, 1)[..., None] * np.array([0.0, 0.9, 0.4])  # very bright red -> hot orange
        out = out * (1 - REDAMT * redness[..., None]) + redcol * REDAMT * redness[..., None]
    else:
        # V2: perceptual tweaks
        # 1) lift input luma with gentle S + mid lift so mids don't sink into mud
        Yl = Y ** 0.85
        Yl = Yl + 0.10 * np.sin(np.pi * Yl) * (Yl - 0.15).clip(0, None) / 0.85
        Yl = Yl.clip(0, 1)
        # 2) highlight shoulder: compress top so highlights roll into gold, not white
        Yl = np.where(Yl > 0.8, 0.8 + 0.2 * (1 - np.exp(-(Yl - 0.8) / 0.2 * 1.3)) / (1 - np.exp(-1.3)), Yl)
        gm = gmap(Yl)
        # 3) skin protection: warm-hue, moderately saturated pixels keep more of their own colour
        mx = rgb.max(-1); mn = rgb.min(-1); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
        skin = ((r > g) & (g > b) & (sat > 0.12) & (sat < 0.65)).astype(float)
        skin *= np.clip((r - g) / np.maximum(mx - mn, 1e-6), 0, 1) ** 0.5  # hue near orange-red
        skin *= np.clip((mx - 0.12) / 0.2, 0, 1)
        # warm(original) re-balanced: keep a little more G so skin stays peach, not red
        warm = np.stack([r * 1.04 + 0.02, g * 0.90 + 0.01, b * 0.50], -1)
        # luma-matched warm so the mix doesn't shift brightness
        wy = 0.2126*warm[...,0] + 0.7152*warm[...,1] + 0.0722*warm[...,2]
        gy = 0.2126*gm[...,0] + 0.7152*gm[...,1] + 0.0722*gm[...,2]
        warm_m = warm * (gy / np.maximum(wy, 1e-4))[..., None] ** 0.6 * (wy / np.maximum(wy,1e-4))[...,None]
        k = 0.72 - 0.22 * skin
        out = k[..., None] * gm + (1 - k[..., None]) * warm_m
    out = out.clip(0, 1)
    R = out[..., 0]; G = np.minimum(out[..., 1], R); B = np.minimum(out[..., 2], G)
    return np.stack([R, G, B], -1)

if __name__ == "__main__":
    dst = sys.argv[1]; variant = sys.argv[2] if len(sys.argv) > 2 else "v2"
    lut = build(variant)
    with open(dst, "w") as f:
        f.write(f'TITLE "fire-lit warm {variant}"\nLUT_3D_SIZE {N}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        for row in lut.reshape(-1, 3): f.write(f"{row[0]:.6f} {row[1]:.6f} {row[2]:.6f}\n")
    flat = lut.reshape(-1, 3)
    print(dst, "entries", len(flat), "max B-R", (flat[:, 2] - flat[:, 0]).max(), "max B-G", (flat[:,2]-flat[:,1]).max())
