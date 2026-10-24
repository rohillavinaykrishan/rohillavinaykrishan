"""MG1 input sync: pulls the upstream plates into assets/plates/ (Chrome-decodable yuv420p H.264),
falling back down a chain when upstream files do not exist yet:
  1. shots/sh010/color/v001/plates/<ID>.mp4            (graded by the Colorist)      -> transcode only
  2. shots/sh010/edit/v001/plates/<ID>.mp4 + color/v001/{tritone,drain}.cube          -> lut3d
  3. shots/sh010/edit/v001/plates/<ID>.mp4 + MG1 temp cube (assets/luts)              -> lut3d
  4. PLACEHOLDER cut straight from source/trailer.mp4 (cues in/out, frame-map conform) + MG1 temp cube, half res
Writes assets/plates/manifest.json. Re-run any time; a plate is rebuilt only when its source changes.
Usage: python3 sync_inputs.py [--force]"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MG1 = os.path.dirname(HERE)
PROJ = os.path.abspath(os.path.join(MG1, "../../../../.."))
SH = os.path.join(PROJ, "shots/sh010")
CUES = json.load(open(os.path.join(SH, "director/v001/cues.json")))
OUT = os.path.join(MG1, "assets/plates")
MAN = os.path.join(OUT, "manifest.json")
FORCE = "--force" in sys.argv
IDS = [s for s in CUES["shots"] if s["layer"] in ("roll_panel", "charge")]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(" ".join(cmd) + "\n" + r.stderr[-1500:])


def probe_ok(p):
    if not os.path.exists(p) or os.path.getsize(p) < 10000:
        return False
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", p], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip().isdigit() and int(r.stdout.strip()) > 0


def sig(p):
    st = os.stat(p)
    return f"{p}|{st.st_size}|{int(st.st_mtime)}"


man = json.load(open(MAN)) if os.path.exists(MAN) else {}
for s in IDS:
    sid, n = s["id"], s["f_out"] - s["f_in"]
    charge = s["layer"] == "charge"
    W, H = (2400, 900) if charge else (2160, 1180)
    graded = os.path.join(SH, "color/v001/plates", sid + ".mp4")
    edit = os.path.join(SH, "edit/v001/plates", sid + ".mp4")
    col_cube = os.path.join(SH, "color/v001", "drain.cube" if charge else "tritone.cube")
    tmp_cube = os.path.join(MG1, "assets/luts", "mg1_temp_drain.cube" if charge else "mg1_temp_tritone.cube")
    dst = os.path.join(OUT, sid + ".mp4")
    if probe_ok(graded):
        mode, src, vf = "graded", graded, f"scale={W}:{H}:flags=lanczos"
    elif probe_ok(edit):
        cube = col_cube if os.path.exists(col_cube) else tmp_cube
        mode = "edit+colorist_cube" if cube == col_cube else "edit+mg1_temp_cube"
        src, vf = edit, f"scale={W}:{H}:flags=lanczos,lut3d=file='{cube}'"
    else:
        mode, src = "placeholder_trailer+mg1_temp_cube", os.path.join(PROJ, "source/trailer.mp4")
        w, h, x, y = map(int, s["crop"].split(":"))
        speed = (s["src_out"] - s["src_in"]) / (n / 25.0)
        pw, ph = W // 2, H // 2
        vf = (f"crop={w}:{h}:{x}:{y},setpts=(PTS-STARTPTS)/{speed:.5f},fps=25,"
              f"scale={pw}:{ph}:force_original_aspect_ratio=increase:flags=lanczos,crop={pw}:{ph},"
              f"lut3d=file='{tmp_cube}'")
    key = sig(src) + "|" + mode + ("|" + sig(col_cube) if mode == "edit+colorist_cube" else "")
    if not FORCE and man.get(sid, {}).get("key") == key and probe_ok(dst):
        continue
    if mode.startswith("placeholder"):
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{s['src_in']:.3f}", "-t", f"{s['src_out'] - s['src_in'] + 0.3:.3f}",
               "-i", src, "-vf", vf, "-frames:v", str(n)]
    else:
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-vf", vf, "-frames:v", str(n)]
    cmd += ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "12",
            "-r", "25", "-movflags", "+faststart", dst]
    run(cmd)
    man[sid] = {"key": key, "mode": mode, "src": os.path.relpath(src, PROJ), "frames": n}
    print(f"{sid}: {mode}")
json.dump(man, open(MAN, "w"), indent=1)
print(json.dumps({k: v["mode"] for k, v in man.items()}, indent=0))
