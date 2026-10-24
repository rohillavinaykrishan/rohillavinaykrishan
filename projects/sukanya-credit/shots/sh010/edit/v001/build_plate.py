#!/usr/bin/env python3
"""Build the ungraded background plate from edl.json (editor, sh010 v001).

usage: vfx-python build_plate.py <project_dir> <out_dir> <work_dir>
"""
import json, math, os, subprocess, sys
import numpy as np, cv2

PROJ, OUT, WORK = sys.argv[1:4]
edl = json.load(open(os.path.join(PROJ, "edl.json")))
FPS = edl["fps"]; NF = edl["frames"]; W, H = 1080, 1920
TRAILER = os.path.join(PROJ, edl["source"])
TFPS = 24000 / 1001
CW = 302  # vertical crop width inside the 1280x536 active picture
cuts = edl["cuts"]


def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def smooth(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def tframes(c):
    return c["transition_in"].get("frames", 0)


# handles: pre = half of the incoming transition, post = half of the next one
for i, c in enumerate(cuts):
    c["pre"] = tframes(c) // 2 if c["transition_in"]["type"] in ("dissolve", "luma_wipe") else 0
    nxt = cuts[i + 1] if i + 1 < len(cuts) else None
    c["post"] = (tframes(nxt) - tframes(nxt) // 2) if nxt and nxt["transition_in"]["type"] in ("dissolve", "luma_wipe") else 0


def to_vertical(img_active, cx, zoom=1.0):
    """img_active: 536x1280 (rgb uint8). crop CW x 536 around cx (sub-pixel), optional centre zoom, scale to 1080x1920."""
    w = CW / zoom; h = 536 / zoom
    x0 = cx - w / 2; y0 = (536 - h) / 2
    sx = W / w; sy = H / h
    # pixel-centre convention (matches ffmpeg/swscale scaling)
    M = np.array([[sx, 0, -x0 * sx + 0.5 * sx - 0.5], [0, sy, -y0 * sy + 0.5 * sy - 0.5]], np.float32)
    return cv2.warpAffine(img_active, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)


# ---- decode all needed native trailer frames (1.0x sync cuts + hero + P4 still) -----------------
def tidx(s):
    return int(math.floor(s * TFPS + 1e-6))

need = set()
for c in cuts:
    if c.get("sync"):
        for f in range(c["frames"][0] - c["pre"], c["frames"][1] + c["post"] + 1):
            need.add(tidx(edl["music"]["in"] + f / FPS))
p4 = next(c for c in cuts if c["id"] == "P4")
need.add(tidx(p4["src_still"]))
need.add(int(round(edl["hero_still"]["src"] * TFPS)))  # hero = nearest trailer frame (3642, pts 151.902)
lo, hi = min(need), max(need)
# decode from 0 without seeking: CFR 23.976, frame k == index k (nb_frames 4046 = 168.75 s * 23.976)
cmd = ["ffmpeg", "-v", "error", "-i", TRAILER, "-an", "-vf", "crop=1280:536:0:92",
       "-fps_mode", "passthrough", "-frames:v", str(hi + 1), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
native = {}
fsz = 1280 * 536 * 3
for k in range(hi + 1):
    buf = p.stdout.read(fsz)
    if len(buf) < fsz: break
    if k in need:
        native[k] = np.frombuffer(buf, np.uint8).reshape(536, 1280, 3).copy()
p.wait()
missing = need - set(native)
assert not missing, f"missing native frames {sorted(missing)[:5]}"
print(f"native frames decoded: {len(native)} ({lo}-{hi})")

# ---- hero still ------------------------------------------------------------------------------
hs = edl["hero_still"]
hero = to_vertical(native[int(round(hs["src"] * TFPS))], hs["cx"])
cv2.imwrite(os.path.join(PROJ, hs["out"]), cv2.cvtColor(hero, cv2.COLOR_RGB2BGR))
# what the plate actually shows on the solve frame 271 (trailer 151.818, the first Chun-Li frame)
h271 = to_vertical(native[tidx(edl["music"]["in"] + 271 / FPS)], hs["cx"])
cv2.imwrite(os.path.join(OUT, "hero_f271_1080.png"), cv2.cvtColor(h271, cv2.COLOR_RGB2BGR))
p4still = to_vertical(native[tidx(p4["src_still"])], p4["cx"])
cv2.imwrite(os.path.join(OUT, "p4_still_1080.png"), cv2.cvtColor(p4still, cv2.COLOR_RGB2BGR))

# ---- slowed cuts: motion-interpolated retime with ffmpeg minterpolate (at crop res) -------------
seg = {}  # id -> dict(frame -> rgb 1080x1920 float)
for c in cuts:
    fa, fb = c["frames"][0] - c["pre"], c["frames"][1] + c["post"]
    frames = {}
    if c["id"] == "P4":
        clip = os.path.join(PROJ, c["source"])
        imgs = []
        if os.path.exists(clip):
            r = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", f"scale={W}:{H}:flags=lanczos",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
            arr = np.frombuffer(r.stdout, np.uint8)
            imgs = list(arr.reshape(-1, H, W, 3))
            print(f"P4: using parallax clip {clip} ({len(imgs)} frames)")
            c["_p4_mode"] = f"parallax ({len(imgs)} frames)"
        if not imgs:
            print("P4: parallax clip missing -> placeholder still with a 1.00-1.04 push")
            c["_p4_mode"] = "placeholder still"
            n = c["frames"][1] - c["frames"][0] + 1
            for i in range(n):
                z = 1.0 + 0.04 * smooth(i / (n - 1))
                imgs.append(to_vertical(native[tidx(p4["src_still"])], p4["cx"], z))
        n = c["frames"][1] - c["frames"][0] + 1
        for f in range(fa, fb + 1):
            i = min(max(f - c["frames"][0], 0), len(imgs) - 1)
            i = int(round(i * (len(imgs) - 1) / max(n - 1, 1))) if len(imgs) != n else i
            frames[f] = imgs[i]
    elif c.get("sync"):
        for f in range(fa, fb + 1):
            s = edl["music"]["in"] + f / FPS
            cx = c["cx"]
            if "cx_pan" in c:
                a, b = c["cx_pan"]["src"]
                cx = c["cx"] + (c["cx_pan"]["to"] - c["cx"]) * smooth((s - a) / (b - a))
            frames[f] = to_vertical(native[tidx(s)], cx)
    else:
        sp = c["speed"]
        s0 = c["src"][0] + (fa - c["frames"][0]) / FPS * sp
        n = fb - fa + 1
        d = os.path.join(WORK, c["id"]); os.makedirs(d, exist_ok=True)
        x0 = c["cx"] - CW // 2
        vf = (f"crop=1280:536:0:92,crop={CW}:536:{x0}:0:exact=1,setpts=(PTS-STARTPTS)/{sp},"
              f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.4f}", "-i", TRAILER, "-an", "-vf", vf,
                        "-frames:v", str(n), os.path.join(d, "f.%04d.png")], check=True)
        for i in range(n):
            im = cv2.cvtColor(cv2.imread(os.path.join(d, f"f.{i + 1:04d}.png")), cv2.COLOR_BGR2RGB)
            z = 1.0
            if c["id"] == "P1":  # push 1.00 -> 1.06 over the cut
                z = 1.0 + 0.06 * min(max((fa + i) / (c["frames"][1]), 0), 1)
            # im is the CW x 536 crop: re-centre on it
            frames[fa + i] = to_vertical(np.pad(im, ((0, 0), (x0, 1280 - CW - x0), (0, 0)), mode="edge"), c["cx"], z)
        print(f"{c['id']}: {n} frames, src {s0:.3f} @ {sp}x")
    seg[c["id"]] = frames

# ---- composite ------------------------------------------------------------------------------
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                        "-frames:v", str(NF), os.path.join(OUT, "bg_plate_raw_1080.mp4")], stdin=subprocess.PIPE)


def f32(x): return x.astype(np.float32) / 255.0


for f in range(NF):
    # owner = the cut whose [start, end] contains f
    oi = next(i for i, c in enumerate(cuts) if c["frames"][0] <= f <= c["frames"][1])
    c = cuts[oi]
    img = f32(seg[c["id"]][f])
    tr = c["transition_in"]; N = tr.get("frames", 0); b = c["frames"][0]
    nxt = cuts[oi + 1] if oi + 1 < len(cuts) else None
    # incoming transition into cut oi (frames b .. b+N-N//2-1) or into next (frames nb-N//2 .. nb-1)
    for tgt, prev in ((c, cuts[oi - 1] if oi > 0 else None), (nxt, c)):
        if tgt is None or prev is None: continue
        t = tgt["transition_in"]; N = t.get("frames", 0); nb = tgt["frames"][0]
        i = f - (nb - N // 2)
        if t["type"] in ("dissolve", "luma_wipe") and 0 <= i < N:
            A = f32(seg[prev["id"]][f]); B = f32(seg[tgt["id"]][f])
            if t["type"] == "dissolve":
                p = (i + 0.5) / N
                img = A * (1 - p) + B * p
            else:
                p = (i + 1) / (N + 1)
                L = cv2.GaussianBlur(B @ np.array([0.2126, 0.7152, 0.0722], np.float32), (0, 0), 6)
                L = (L - L.min()) / max(L.max() - L.min(), 1e-6)
                s = 0.35
                a = np.clip((p * (1 + s) - (1 - L)) / s, 0, 1)[..., None]
                img = A * (1 - a) + B * a
        elif t["type"] in ("flash", "flare"):
            st = t["strength"]; col = hexrgb(t["color"])
            if t["type"] == "flash":
                i = f - nb
            else:
                i = f - (nb - N // 2)
            if 0 <= i < len(st):
                w = st[i]
                img = 1 - (1 - img) * (1 - col * w)  # screen
    enc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
json.dump({"p4": p4.get("_p4_mode")}, open(os.path.join(OUT, "build_info.json"), "w"))
print("done", p4.get("_p4_mode"))
