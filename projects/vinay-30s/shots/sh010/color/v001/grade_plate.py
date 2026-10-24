#!/usr/bin/env python3
"""Grade editor plates with the SPECTRUM LUTs. grade_plate.py ID [ID...] [--src DIR] [--dst DIR]
 DUO:  bt709->RGB, per-plate levels lift (constant over the shot), grain noise=alls=6:allf=t, lut3d duo_<fighter>.cube
 TRUE: optional constant pre-LUT warm balance (only if a frame fails R>=B), lut3d true.cube
 TRUE>DRAIN (C6): true.cube -> drain.cube, smoothstep blend over the shot (fully drained on the last frame)
 Tiles T1-T8: <ID>_duo.mp4 and <ID>_true.mp4.  Out: H.264 crf 10 yuv420p BT.709 tv, 25 fps, same frame count."""
import argparse, json, os, subprocess, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import qc_rgb
PROJ = os.path.abspath(os.path.join(HERE, "../../../.."))
CUES = json.load(open(os.path.join(HERE, "../../director/v001/cues.json")))
SLUG = {"Ryu": "ryu", "Ken": "ken", "Dhalsim": "dhalsim", "Blanka": "blanka", "Guile": "guile",
        "Chun-Li": "chunli", "M. Bison": "bison", "E. Honda": "honda"}
IN = "scale=in_color_matrix=bt709:in_range=tv:out_color_matrix=bt709:out_range=pc,format=gbrp"
OUT = "scale=in_range=pc:out_color_matrix=bt709:out_range=tv,format=yuv420p"
LUT = lambda n: f"lut3d=file={os.path.join(HERE, n)}:interp=tetrahedral"

def nframes(f):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                               "stream=nb_read_frames", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())

def encode(src, vf, dst):
    tmp = dst + ".tmp.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", vf, "-map", "[o]", "-an", "-fps_mode", "passthrough",
           "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", "-threads", "2",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
           "-movflags", "+faststart", tmp]
    subprocess.run(cmd, check=True); os.replace(tmp, dst)

def duo_levels(src):
    a = qc_rgb.frames(src, 320).astype(np.float32) / 255
    y = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    lo, hi = np.percentile(y, 0.5), np.percentile(y, 99.5)
    imin = float(np.clip(lo, 0, 0.08)); imax = float(np.clip(hi, 0.62, 1.0))
    # midtone lift for dark plates: bring the 60th-percentile luma (faces sit around there) up to >= 0.32
    p = float(np.clip((np.percentile(y, 60) - imin) / (imax - imin), 1e-3, 1))
    gamma = float(np.clip(np.log(0.32) / np.log(p), 0.55, 1.0)) if p < 0.32 else 1.0
    return imin, imax, gamma

def grade_duo(src, dst, fighter):
    imin, imax, gm = duo_levels(src)
    e = f"255*pow(clip((val/255-{imin:.4f})/{imax - imin:.4f}\\,0\\,1)\\,{gm:.3f})"
    lv = f"lutrgb=r='{e}':g='{e}':b='{e}'"
    vf = f"[0:v]{IN},{lv},noise=alls=6:allf=t,{LUT('duo_' + SLUG[fighter] + '.cube')},{OUT}[o]"
    encode(src, vf, dst); return f"duo:{fighter} levels {imin:.3f}-{imax:.3f} gamma {gm:.2f}"

def grade_true(src, dst, drain=False, local=False):
    for k in ((0.0,) if local else (0.0, 0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21, 0.24, 0.27, 0.30)):
        wb = f"colorchannelmixer=rr={1 + k:.3f}:gg={1 - k / 4:.3f}:bb={1 - k:.3f}," if k else ""
        if drain:
            n = nframes(src) - 1
            w = f"min(N/{n},1)"; ss = f"(3*pow({w},2)-2*pow({w},3))"
            vf = (f"[0:v]{IN},{wb}split[a][b];[a]{LUT('true.cube')}[t];[b]{LUT('drain.cube')}[d];"
                  f"[t][d]blend=all_expr='A+(B-A)*{ss}',{OUT}[o]")
        else:
            vf = f"[0:v]{IN},{wb}{LUT('true.cube')},{OUT}[o]"
        encode(src, vf, dst)
        a = qc_rgb.frames(dst).astype(np.float32); d = a[..., 0].mean((1, 2)) - a[..., 2].mean((1, 2))
        if local: return "true (T5-T7 local exemption, no warm-pre)"
        if d.min() >= 0.5: return ("true>drain" if drain else "true") + (f" warm-pre rr+{k:.2f} gg-{k/4:.3f} bb-{k:.2f}" if k else "")
    return ("true>drain" if drain else "true") + f" warm-pre {k:.2f} STILL FAILS min(R-B)={d.min():.2f}"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ids", nargs="+")
    ap.add_argument("--src", default=os.path.join(PROJ, "shots/sh010/edit/v001/plates"))
    ap.add_argument("--dst", default=os.path.join(HERE, "plates"))
    a = ap.parse_args(); os.makedirs(a.dst, exist_ok=True)
    shots = {s["id"]: s for s in CUES["shots"]}; tiles = {t["id"]: t for t in CUES["tiles"]}
    for i in a.ids:
        src = os.path.join(a.src, i + ".mp4"); n_in = nframes(src)
        if i in shots:
            g = shots[i]["grade"]; dst = os.path.join(a.dst, i + ".mp4")
            how = grade_duo(src, dst, g.split(":", 1)[1]) if g.startswith("duo:") else grade_true(src, dst, drain=(g == "true>drain"))
            outs = [(dst, how)]
        elif i in tiles:
            d1 = os.path.join(a.dst, i + "_duo.mp4"); d2 = os.path.join(a.dst, i + "_true.mp4")
            outs = [(d1, grade_duo(src, d1, tiles[i]["character"])), (d2, grade_true(src, d2, local=i in ("T5", "T6", "T7")))]
        else:
            print("unknown id", i); continue
        for dst, how in outs:
            n_out = nframes(dst)
            line = f"{os.path.basename(dst)}: {how}; frames in {n_in} out {n_out} {'OK' if n_in == n_out else 'MISMATCH'}"
            print(line); open(os.path.join(HERE, "grade_log.txt"), "a").write(line + "\n")

if __name__ == "__main__":
    main()
