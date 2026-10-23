#!/usr/bin/env python3
"""SPECTRUM colour QC (treatment 5.4): every frame mean R >= mean B, except the designed blue/violet
roster beats f121-196 (R5-R7) and the T5-T7 DUO tiles (local only). Also reports floor (< Ink #07060A)
and 255-clipping as warnings.
  qc_rgb.py plates/R5.mp4 plates/F3.mp4 ...        # plate ID read from the file name, master frames from cues.json
  qc_rgb.py --master master.mp4                      # frame index = master frame
  qc_rgb.py --f-in 365 some.mp4                      # explicit master frame of the file's first frame
Exit 0 = all pass, 1 = any fail."""
import argparse, json, os, re, subprocess, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CUES = os.path.join(HERE, "../../director/v001/cues.json")
EXCEPT = (121, 196)                     # master frames, inclusive
LOCAL_ONLY = {"T5_duo", "T6_duo", "T7_duo"}

def probe(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip().split(",")
    return int(o[0]), int(o[1])

def frames(f, maxw=480):
    w, h = probe(f)
    if w > maxw: h = int(round(h * maxw / w / 2) * 2); w = maxw
    cmd = ["ffmpeg", "-v", "error", "-i", f, "-vf", f"scale={w}:{h}:flags=area:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
           "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)

def plate_f_in(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    base = re.sub(r"_(duo|true)$", "", stem)
    cues = json.load(open(CUES))
    for s in cues["shots"]:
        if s["id"] == base: return s["f_in"], stem
    for t in cues["tiles"]:
        if t["id"] == base: return (686 if stem.endswith("_true") else t["arrive_f"]), stem
    return None, stem

def check(path, f_in=None, master=False):
    stem = os.path.splitext(os.path.basename(path))[0]
    if master: f_in = 0
    elif f_in is None: f_in, stem = plate_f_in(path)
    a = frames(path).astype(np.float32)
    mR, mB = a[..., 0].mean((1, 2)), a[..., 2].mean((1, 2))
    diff = mR - mB
    luma = a @ np.array([0.2126, 0.7152, 0.0722], np.float32); luma = luma.mean((1, 2))
    fails, exempt, ink = [], 0, 0          # ink: near-black frame (mean luma < 16) whose B>R is only Ink's own +3
    for i, d in enumerate(diff):
        mf = None if f_in is None else f_in + i
        is_ex = stem in LOCAL_ONLY or (mf is not None and EXCEPT[0] <= mf <= EXCEPT[1])
        if is_ex: exempt += 1
        elif d < 0 and not (luma[i] < 16 and d >= -3.0): fails.append((i, mf, round(float(d), 2)))
        elif d < 0: ink += 1
    px = a.reshape(len(a), -1, 3)
    below = float((px.max(-1) < 4).mean() * 100)      # % pixels darker than Ink (all channels < 4); palette stops legitimately have 0 in one channel
    clip = float((px.min(-1) >= 254).mean() * 100)    # % pixels clipped to white (all channels >= 254); White Hot itself is 255,248,236
    ok = not fails
    print(f"{'PASS' if ok else 'FAIL'}  {stem:10s} frames={len(a):3d} master_f_in={f_in} min(R-B)={diff.min():+7.2f} "
          f"mean(R-B)={diff.mean():+6.2f} exempt={exempt} ink={ink} below_ink={below:.3f}% white_clip={clip:.3f}%"
          + ("  WARN" if below > 0.1 or clip > 0.5 else "")
          + (f"  failing(plate_i,master_f,R-B)={fails[:8]}{'...' if len(fails) > 8 else ''}" if fails else ""))
    return ok, float(diff.min())

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="+")
    ap.add_argument("--master", action="store_true"); ap.add_argument("--f-in", type=int)
    a = ap.parse_args()
    res = [check(f, a.f_in, a.master)[0] for f in a.files]
    sys.exit(0 if all(res) else 1)
