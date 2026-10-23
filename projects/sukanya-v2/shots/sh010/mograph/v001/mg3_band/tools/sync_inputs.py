#!/usr/bin/env python3
"""MG3 (band chain, master f261-349) input sync. Re-run any time; it rebuilds what changed.

Builds, inside mg3_band/assets/:
  plates/B01..B08.mp4   band plates, 2400x900, 25 fps, exact frame counts, UNLOCK grade baked in.
                        Source chain (first that exists with the right frame count):
                          1. color/v001/plates/<ID>.mp4             (Colorist graded)  -> transcode only
                          2. edit/v001/plates/<ID>.mp4 + color/v001/band_<ID>.cube | band.cube
                          3. edit/v001/plates/<ID>.mp4 + assets/luts/band.cube (made with the Colorist's make_luts.py)
                          4. PLACEHOLDER cut from source/trailer.mp4 (cues in/out, frame-map conform) + band LUT
  echo/B01..B07.jpg     tritone still of each shot's LAST frame (the afterimage shown in the echo bands
                        while the next shot plays), 2400x900.
  pop/B02_0..7.png, pop/B03_0..7.png   roto pop-out frames: band-graded plate x roto matte, RGBA 2400x900.
                        Matte = roto/v001/<ID>_matte.webm (alpha channel if it has one, else luma).
                        No matte yet -> fully transparent PNGs (pop-out invisible, comp still valid).
  manifest.json         what each asset was built from.
Usage: python3 sync_inputs.py [--force]
"""
import json, os, subprocess, sys, importlib.util, shutil, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.dirname(HERE)
PROJ = os.path.abspath(os.path.join(MG, "../../../../.."))
SH = os.path.join(PROJ, "shots/sh010")
CUES = json.load(open(os.path.join(SH, "director/v001/cues.json")))
A = os.path.join(MG, "assets")
FORCE = "--force" in sys.argv
SHOTS = {s["id"]: s for s in CUES["shots"] if s["layer"] == "super_band"}
POPS = {"B02": 279, "B03": 290}   # first master frame of each 8-frame pop-out window
POP_N = 8
os.makedirs(os.path.join(HERE, "luts"), exist_ok=True)
for d in ("plates", "echo", "pop"):
    os.makedirs(os.path.join(A, d), exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(" ".join(cmd) + "\n" + r.stderr[-2000:])
    return r.stdout


def nframes(p):
    if not os.path.exists(p) or os.path.getsize(p) < 2000:
        return -1
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", p], capture_output=True, text=True)
    s = r.stdout.strip().split(",")[0]
    return int(s) if s.isdigit() else -1


def sig(p):
    st = os.stat(p)
    return f"{os.path.relpath(p, PROJ)}|{st.st_size}|{int(st.st_mtime)}"


# --- LUTs: the Colorist's files win; else build ours with the Colorist's own script (read-only import) ---
spec = importlib.util.spec_from_file_location("colorist_luts", os.path.join(SH, "color/v001/make_luts.py"))
CL = importlib.util.module_from_spec(spec); spec.loader.exec_module(CL)
own_band = os.path.join(HERE, "luts/band.cube")
own_tri = os.path.join(HERE, "luts/tritone.cube")
if not os.path.exists(own_band):
    CL.write_cube(own_band, CL.band)
if not os.path.exists(own_tri):
    CL.write_cube(own_tri, CL.tritone)


def band_cube(sid):
    for c in (os.path.join(SH, f"color/v001/band_{sid}.cube"), os.path.join(SH, "color/v001/band.cube")):
        if os.path.exists(c):
            return c, "colorist:" + os.path.basename(c)
    return own_band, "mg3_copy_of_colorist_band()"


tri_cube = os.path.join(SH, "color/v001/tritone.cube")
tri_cube = tri_cube if os.path.exists(tri_cube) else own_tri

MAN = os.path.join(A, "manifest.json")
man = json.load(open(MAN)) if os.path.exists(MAN) else {}

for sid, s in SHOTS.items():
    n = s["f_out"] - s["f_in"]
    graded = os.path.join(SH, "color/v001/plates", sid + ".mp4")
    edit = os.path.join(SH, "edit/v001/plates", sid + ".mp4")
    dst = os.path.join(A, "plates", sid + ".mp4")
    raw_src = None  # ungraded source used for the echo still
    if nframes(graded) == n:
        mode, src, vf = "graded", graded, "scale=2400:900:flags=lanczos"
        raw_src = edit if nframes(edit) == n else graded
    elif nframes(edit) == n:
        cube, cname = band_cube(sid)
        mode, src, vf = "edit+" + cname, edit, f"scale=2400:900:flags=lanczos,lut3d=file='{cube}'"
        raw_src = edit
    else:
        cube, cname = band_cube(sid)
        mode, src = "PLACEHOLDER_trailer+" + cname, os.path.join(PROJ, "source/trailer.mp4")
        w, h, x, y = map(int, s["crop"].split(":"))
        speed = (s["src_out"] - s["src_in"]) / (n / 25.0)
        vf = (f"crop={w}:{h}:{x}:{y},setpts=(PTS-STARTPTS)/{speed:.5f},fps=25,"
              f"scale=2400:1005:flags=lanczos,crop=2400:900:0:52,lut3d=file='{cube}'")
    key = sig(src) + "|" + mode
    if FORCE or man.get(sid, {}).get("key") != key or nframes(dst) != n:
        if mode.startswith("PLACEHOLDER"):
            cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{s['src_in']:.3f}",
                   "-t", f"{s['src_out'] - s['src_in'] + 0.3:.3f}", "-i", src, "-vf", vf, "-frames:v", str(n)]
        else:
            cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-vf", vf, "-frames:v", str(n)]
        cmd += ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
                "-g", "1", "-r", "25", "-movflags", "+faststart", dst]   # all-intra: exact seeks
        run(cmd)
        # echo still = tritone of the shot's last frame
        tmp = os.path.join(A, "echo", sid + "_last.png")
        if raw_src and raw_src != graded:
            run(["ffmpeg", "-y", "-v", "error", "-i", raw_src, "-vf",
                 f"select=eq(n\\,{n-1}),scale=2400:900,lut3d=file='{tri_cube}'", "-frames:v", "1", tmp])
        else:
            run(["ffmpeg", "-y", "-v", "error", "-i", dst, "-vf",
                 f"select=eq(n\\,{n-1}),lut3d=file='{tri_cube}'", "-frames:v", "1", tmp])
        Image.open(tmp).convert("RGB").save(os.path.join(A, "echo", sid + ".jpg"), quality=88)
        os.remove(tmp)
        man[sid] = {"key": key, "mode": mode, "src": os.path.relpath(src, PROJ), "frames": n}
        print(f"{sid}: {mode}")

# --- roto pop-outs ---
for sid, f0 in POPS.items():
    s = SHOTS[sid]
    matte = os.path.join(SH, "roto/v001", sid + "_matte.webm")
    plate = os.path.join(A, "plates", sid + ".mp4")
    key = (sig(matte) if os.path.exists(matte) else "none") + "|" + man[sid]["key"]
    outs = [os.path.join(A, "pop", f"{sid}_{i}.png") for i in range(POP_N)]
    if not FORCE and man.get(sid + "_pop", {}).get("key") == key and all(map(os.path.exists, outs)):
        continue
    if not os.path.exists(matte):
        for o in outs:
            Image.new("RGBA", (2400, 900), (0, 0, 0, 0)).save(o)
        man[sid + "_pop"] = {"key": key, "mode": "NO_MATTE_YET (transparent)"}
        print(f"{sid}_pop: no matte yet")
        continue
    tmpd = tempfile.mkdtemp(dir=os.path.join(A, "pop"))
    pf = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=pix_fmt:stream_tags=alpha_mode",
              "-of", "json", matte])
    has_alpha = "yuva" in pf or '"alpha_mode": "1"' in pf
    dec = ["-c:v", "libvpx-vp9"] if has_alpha else []
    mvf = "alphaextract," if has_alpha else "format=gray,"
    run(["ffmpeg", "-y", "-v", "error", *dec, "-i", matte, "-vf", mvf + "scale=2400:900", os.path.join(tmpd, "m%03d.png")])
    run(["ffmpeg", "-y", "-v", "error", "-i", plate, os.path.join(tmpd, "p%03d.png")])
    nm = len([f for f in os.listdir(tmpd) if f.startswith("m")])
    for i, o in enumerate(outs):
        fi = (f0 - s["f_in"]) + i                      # plate frame index for this pop frame
        mi = min(fi, nm - 1)                           # matte assumed frame-aligned with the plate
        p = np.asarray(Image.open(os.path.join(tmpd, f"p{fi+1:03d}.png")).convert("RGB"))
        m = np.asarray(Image.open(os.path.join(tmpd, f"m{mi+1:03d}.png")).convert("L"))
        Image.fromarray(np.dstack([p, m])).save(o)
    shutil.rmtree(tmpd)
    man[sid + "_pop"] = {"key": key, "mode": "roto" + (" (alpha)" if has_alpha else " (luma)"), "matte_frames": nm}
    print(f"{sid}_pop: roto matte applied ({nm} matte frames)")

json.dump(man, open(MAN, "w"), indent=1)
print(json.dumps({k: v["mode"] for k, v in man.items()}, indent=0))
