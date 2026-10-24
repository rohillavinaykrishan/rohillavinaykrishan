#!/usr/bin/env python3
"""Prepare composition inputs for sh010 mograph v001 ("PARALLAX").

- source/credits.txt          -> assets/credits.js  (verbatim names, re-read every run)
- color/v001/bg_plate_1080.mp4 -> assets/bg_plate_1080.mp4 (placeholder from assets/ph/ if missing)
- color/v001/sf_logo_silver.png -> assets/sf_logo_silver.png (placeholder if missing)
- roto/v001/points.json        -> assets/points.js  (placeholder cloud from assets/ph/hero_1080.png if missing)

Usage: python3 prep.py   (prints which inputs are REAL vs PLACEHOLDER)
"""
import json, os, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "../../../.."))
SHOT = os.path.join(PROJ, "shots/sh010")
A = os.path.join(HERE, "assets")
PH = os.path.join(A, "ph")
status = {}


def credits():
    rows = []
    with open(os.path.join(PROJ, "source/credits.txt"), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip():
                continue
            if "|" in line:
                l, r = line.split("|", 1)
            else:
                l, r = line, ""
            rows.append([l.strip(), r.strip()])
    with open(os.path.join(A, "credits.js"), "w", encoding="utf-8") as f:
        f.write("window.CREDITS = " + json.dumps(rows, ensure_ascii=False) + ";\n")
    n = sum(1 for r in rows for x in r if x)
    status["credits"] = f"{len(rows)} rows, {n} names, row1={rows[0]}"


def nframes(path):
    import subprocess
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return int(r.stdout.strip().split(",")[0])
    except ValueError:
        return -1


def copy_or_ph(src_rel, name):
    src = os.path.join(SHOT, src_rel)
    dst = os.path.join(A, name)
    ok = os.path.isfile(src) and os.path.getsize(src) > 0
    if ok and name.endswith(".mp4"):
        n = nframes(src)
        if n != 375:
            status[name + "_warn"] = f"REAL file has {n} frames (need 375) - using placeholder"
            ok = False
    if ok:
        if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst) or os.path.getsize(src) != os.path.getsize(dst):
            shutil.copy2(src, dst)
        status[name] = "REAL " + src
    else:
        shutil.copy2(os.path.join(PH, name), dst)
        status[name] = "PLACEHOLDER"


def _norm_points(raw):
    """Return Nx4 array (u_px, v_px, depth01 [0 near..1 far], lum01) in 1080x1920 pixel space."""
    meta = {}
    pts = raw
    if isinstance(raw, dict):
        meta = raw
        for k in ("points", "pts", "data", "cloud"):
            if k in raw:
                pts = raw[k]
                break
    W = float(meta.get("width", meta.get("w", 1080)))
    H = float(meta.get("height", meta.get("h", 1920)))
    rows = []
    for p in pts:
        if isinstance(p, dict):
            u = p.get("u", p.get("x"))
            v = p.get("v", p.get("y"))
            d = p.get("depth", p.get("d", p.get("z", 0.5)))
            l = p.get("lum", p.get("l", p.get("luminance", p.get("luma", 0.7))))
        else:
            u, v = p[0], p[1]
            d = p[2] if len(p) > 2 else 0.5
            l = p[3] if len(p) > 3 else 0.7
        rows.append([float(u), float(v), float(d), float(l)])
    a = np.array(rows, dtype=np.float64)
    if a[:, 0].max() <= 1.001 and a[:, 1].max() <= 1.001:  # normalised uv
        a[:, 0] *= W
        a[:, 1] *= H
    elif W != 1080:
        a[:, 0] *= 1080.0 / W
        a[:, 1] *= 1920.0 / H
    # depth -> 0..1, unknown convention: normalise range; depth.py maps are "bright = near"
    d = a[:, 2]
    lo, hi = np.percentile(d, 1), np.percentile(d, 99)
    dn = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
    conv = meta.get("depth_convention", meta.get("depth_mode", "near_high"))
    if isinstance(conv, str) and ("far_high" in conv or "metric" in conv or "distance" in conv):
        a[:, 2] = dn
    else:
        a[:, 2] = 1.0 - dn  # bright/large = near -> small depth01
    l = a[:, 3]
    if l.max() > 1.5:
        l = l / 255.0
    a[:, 3] = np.clip(l, 0, 1)
    return a


def placeholder_points():
    from PIL import Image
    im = np.asarray(Image.open(os.path.join(PH, "hero_1080.png")).convert("L"), dtype=np.float64) / 255.0
    H, W = im.shape
    gx = np.zeros_like(im); gy = np.zeros_like(im)
    gx[1:-1, 1:-1] = (im[1:-1, 2:] - im[1:-1, :-2]) * 2 + (im[:-2, 2:] - im[:-2, :-2]) + (im[2:, 2:] - im[2:, :-2])
    gy[1:-1, 1:-1] = (im[2:, 1:-1] - im[:-2, 1:-1]) * 2 + (im[2:, :-2] - im[:-2, :-2]) + (im[2:, 2:] - im[:-2, 2:])
    mag = np.hypot(gx, gy)
    thr = np.percentile(mag, 94)
    ys, xs = np.nonzero(mag > thr)
    rng = np.random.default_rng(7)
    idx = rng.choice(len(xs), size=min(2800, len(xs)), replace=False)
    ex, ey = xs[idx], ys[idx]
    rx = rng.integers(0, W, 600); ry = rng.integers(0, H, 600)
    u = np.concatenate([ex, rx]).astype(float); v = np.concatenate([ey, ry]).astype(float)
    # fake depth: blurred luminance (bright = near), coarse
    from PIL import ImageFilter
    blur = np.asarray(Image.open(os.path.join(PH, "hero_1080.png")).convert("L").filter(ImageFilter.GaussianBlur(40)), dtype=np.float64) / 255.0
    d = 1.0 - blur[v.astype(int), u.astype(int)]
    l = im[v.astype(int), u.astype(int)]
    return np.stack([u, v, d, l], 1)


def to_screen(a):
    """generic Nx4 (u1080, v1080, depth01, lum) -> (sx4k, sy4k, Zc, lum)"""
    b = a.copy()
    b[:, 0] *= 2.0; b[:, 1] *= 2.0
    b[:, 2] = 2700.0 + b[:, 2] * 2500.0
    return b


def points():
    src = os.path.join(SHOT, "roto/v002/points.json")
    if not os.path.isfile(src):
        status["points_warn"] = "roto/v002/points.json missing - falling back to v001 (built from 151.902 = frame 273)"
        src = os.path.join(SHOT, "roto/v001/points.json")
    if os.path.isfile(src):
        with open(src) as f:
            raw = json.load(f)
        if isinstance(raw, dict) and "z_near" in raw and "f" in raw:
            # roto format: screen px at w x h (4K), camera depth Zc, lum
            sc = 2160.0 / float(raw.get("w", 2160))
            a = np.array([[p[0] * sc, p[1] * sc, p[2], p[3]] for p in raw["points"]], dtype=np.float64)
            f_src = float(raw["f"])
            if abs(f_src - 2600.0) > 1e-3:
                status["points_warn"] = f"f={f_src} != 2600"
        else:
            a = to_screen(_norm_points(raw))
        status["points"] = f"REAL {src} ({len(a)} pts)"
    else:
        a = to_screen(placeholder_points())
        status["points"] = f"PLACEHOLDER ({len(a)} pts)"
    flat = np.round(a, 3).tolist()
    with open(os.path.join(A, "points.js"), "w") as f:
        f.write("window.POINTS = " + json.dumps(flat, separators=(",", ":")) + ";\n")


credits()
copy_or_ph("color/v001/bg_plate_1080.mp4", "bg_plate_1080.mp4")
copy_or_ph("color/v001/sf_logo_silver.png", "sf_logo_silver.png")
points()
for k, v in status.items():
    print(f"{k:22s} {v}")
