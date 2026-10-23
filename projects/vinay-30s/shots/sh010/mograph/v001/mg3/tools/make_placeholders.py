#!/usr/bin/env python3
"""MG3 placeholder plates (used only until edit/ or color/ plates land).
Low-res conforms from source/trailer.mp4 per cues.json: F1-F9 window plates (720x302),
tiles T1-T8 as _duo (sRGB piecewise gradient map, approximate) and _true (240x214), 40 f."""
import json, subprocess, os, sys
P = "/home/user/rohillavinaykrishan/projects/vinay-30s"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "placeholders")
cues = json.load(open(f"{P}/shots/sh010/director/v001/cues.json"))
SRC = f"{P}/source/trailer.mp4"
INK = (7, 6, 10); WHITE = (255, 248, 236)

def hx(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

def duo_expr(hue):
    h = hx(hue); dark = tuple(int(c*0.38) for c in h)
    mix = tuple(int(h[i]*0.55 + WHITE[i]*0.45) for i in range(3))
    stops = [(0, INK), (71.4, dark), (153, h), (219.3, mix), (255, WHITE)]
    ex = []
    for ch in range(3):
        e = str(WHITE[ch])
        for (a, ca), (b, cb) in reversed(list(zip(stops[:-1], stops[1:]))):
            seg = f"{ca[ch]}+({cb[ch]-ca[ch]})*(val-{a})/{b-a}"
            e = f"if(lt(val\\,{b})\\,{seg}\\,{e})"
        ex.append(e)
    return f"format=gray,format=rgb24,lutrgb=r='{ex[0]}':g='{ex[1]}':b='{ex[2]}'"

def run(ss, frames, speed, crop, scale, extra, out):
    if os.path.exists(out) and "--force" not in sys.argv: return
    vf = f"crop={crop},setpts=(PTS-STARTPTS)/{speed},fps=25,scale={scale}:flags=lanczos"
    if extra: vf += "," + extra
    vf += ",format=yuv420p"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-i", SRC, "-vf", vf,
                    "-frames:v", str(frames), "-an", "-c:v", "libx264", "-crf", "18",
                    "-preset", "fast", "-r", "25", out], check=True)

for s in cues["shots"]:
    if s["id"].startswith("F"):
        run(s["src_in"], s["f_out"] - s["f_in"], s["speed"], s["crop"], "720:302", "",
            f"{OUT}/{s['id']}.mp4")
for t in cues["tiles"]:
    for kind in ("true", "duo"):
        run(t["src_in"], t["clip_frames"], t["speed"], t["crop"], "240:214",
            duo_expr(t["hue"]) if kind == "duo" else "", f"{OUT}/{t['id']}_{kind}.mp4")
print("ok")
