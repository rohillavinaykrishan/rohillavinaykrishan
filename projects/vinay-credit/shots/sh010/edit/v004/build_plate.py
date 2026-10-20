#!/usr/bin/env python3
"""Build the background plate from edl.json. Usage: build_plate.py <project_dir> <out.mp4> [--proxy]
Prints nothing but runs ffmpeg. Plate = ungraded (raw); grading is a separate pass (assemble.sh)."""
import json, subprocess, sys, os
proj, out = sys.argv[1], sys.argv[2]
proxy = "--proxy" in sys.argv
grade = "--grade" in sys.argv
edl = json.load(open(os.path.join(proj, "edl.json")))
FPS = edl["fps"]; W, H = (540, 960) if proxy else (1080, 1920)
SRC = os.path.join(proj, "source/trailer.mp4")
cuts = edl["cuts"]
args = ["ffmpeg", "-y", "-v", "error", "-nostats"]
fg = []
for i, c in enumerate(cuts):
    f0, f1 = c["clip_render_frames"]; n = f1 - f0; sp = c["speed"]
    span = (n - 1) * sp / FPS
    args += ["-ss", f'{c["src_in_at_first_frame"]:.3f}', "-t", f"{span + 0.25:.3f}", "-i", SRC]
    cx = c["crop_cx"]
    if isinstance(cx, str):  # "pan a -> b"
        a, b = [float(v) for v in cx.replace("pan", "").split("(")[0].split("->")]
        dur = span if span > 0 else 1
        xexpr = f"'{a}-151+({b}-{a})*min(max(t/{dur:.4f},0),1)'"
    else:
        xexpr = str(int(cx) - 151)
    chain = [f"[{i}:v]crop=1280:536:0:92", f"crop=302:536:{xexpr}:0",
             f"setpts=(PTS-STARTPTS)/{sp}",
             f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=fdiff:scd_threshold=8",
             f"trim=end_frame={n}", "setpts=N/(%d*TB)" % FPS,
             f"scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int"]
    mv = c.get("move", "")
    if "push-in" in mv:
        z1 = float(mv.split("->")[1].split()[0]); dz = z1 - 1.0
        chain += [f"scale=w='2*trunc({W}*(1+{dz}*n/{n-1})/2)':h=-2:eval=frame:flags=lanczos",
                  f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2"]
    chain += ["unsharp=5:5:0.45:5:5:0.0", "setsar=1", "format=yuv420p"]
    if grade and c.get("grade_trim"):
        chain += [c["grade_trim"]]
    nn = n
    if "freeze" in c:
        hold = c["freeze"]["hold_frames"][1] - c["freeze"]["hold_frames"][0] - 1
        chain += [f"tpad=stop_mode=clone:stop={hold}"]
        nn = n + hold
    if c["transition_in"]["type"].startswith("cut + gold flash"):
        mix = c["transition_in"]["flash_white_mix"]
        k = "+".join(f"eq(round(T*{FPS}),{j})*{m}" for j, m in enumerate(mix))
        fg.append(",".join(chain) + f"[j{i}];color=c=white:s={W}x{H}:r={FPS},format=yuv420p,trim=end_frame={nn}[w{i}];"
                  f"[j{i}][w{i}]blend=all_expr='A+(B-A)*({k})':shortest=1,format=yuv420p[v{i}]")
    else:
        fg.append(",".join(chain) + f"[v{i}]")
# xfade chain for every clip whose transition is an xfade; hard cut (concat) otherwise
leaks = []
cur = "v0"; cur_len = cuts[0]["clip_render_frames"][1] - cuts[0]["clip_render_frames"][0]
for i in range(1, len(cuts)):
    t = cuts[i]["transition_in"]; n = cuts[i]["clip_render_frames"][1] - cuts[i]["clip_render_frames"][0]
    if "freeze" in cuts[i]:
        n += cuts[i]["freeze"]["hold_frames"][1] - cuts[i]["freeze"]["hold_frames"][0] - 1
    if "xfade_offset_frame" in t:
        d = t["frames"]; off = t["xfade_offset_frame"]
        assert off == cur_len - d, (cuts[i]["id"], off, cur_len, d)
        if t["type"] == "leak":
            leaks.append((t["beat_frame"], t["leak"]))
        xt = "fade" if t["type"] == "leak" else t["type"]
        fg.append(f"[{cur}][v{i}]xfade=transition={xt}:duration={d/FPS:.4f}:offset={off/FPS:.4f}[x{i}]")
        cur_len = cur_len + n - d
    else:
        assert cur_len == cuts[i]["frames"][0], (cuts[i]["id"], cur_len)
        fg.append(f"[{cur}][v{i}]concat=n=2:v=1:a=0[x{i}]")
        cur_len += n
    cur = f"x{i}"
assert cur_len == edl["frames"], cur_len
post = ""
if grade:
    cdir = os.path.join(proj, "shots/sh010/color/v001")
    finish = open(os.path.join(cdir, "finish_filter.txt")).read().strip()
    if proxy: finish = finish.replace("gblur=sigma=3", "gblur=sigma=1.5")
    post = f",format=gbrp,lut3d=file={os.path.join(cdir, 'warm.cube')}:interp=tetrahedral,{finish}"
fg.append(f"[{cur}]settb=1/{FPS},setpts=N,fps={FPS},format=gbrp[p0]")
import numpy as np
from PIL import Image
here = os.path.dirname(os.path.abspath(out))
for k, (b, lk) in enumerate(leaks):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ox, oy = {"left": (-0.15*W, 0.35*H), "right": (1.15*W, 0.45*H), "top-right": (1.1*W, -0.05*H)}[lk["side"]]
    R = 1.15 * W if lk["side"] != "top-right" else 1.0 * H
    m = np.clip(1 - np.hypot(xx-ox, yy-oy)/R, 0, 1) ** 1.6
    col = np.array([255, 214, 160], np.float32)
    png = os.path.join(here, f"leak_{lk['side']}_{W}.png")
    Image.fromarray((m[..., None]*col).round().astype(np.uint8)).save(png)
    args += ["-loop", "1", "-framerate", str(FPS), "-t", str(edl["duration"]), "-i", png]
    li = len(cuts) + k; pk = lk["peak"]
    env = f"{pk}*pow(max(0,1-abs(T*{FPS}-{b})/6),1.3)"
    fg.append(f"[{li}:v]format=gbrp,setpts=N/({FPS}*TB)[l{k}];[p{k}][l{k}]blend=all_expr='A+(255-A)*(B/255)*{env}':enable='between(n,{b-6},{b+6})'[p{k+1}]")
fg.append(f"[p{len(leaks)}]format=yuv420p{post}[out]")
args += ["-filter_complex", ";".join(fg), "-map", "[out]", "-an", "-frames:v", str(edl["frames"]),
         "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-movflags", "+faststart", out]
open(out + ".cmd.txt", "w").write(" ".join(a if " " not in a else repr(a) for a in args) + "\n")
subprocess.run(args, check=True)
