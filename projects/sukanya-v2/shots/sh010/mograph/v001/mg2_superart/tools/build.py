"""MG2 SUPER ART FX build (master f243-f276). Regenerates the HyperFrames project from upstream files.
  - her row + every visible roll row at f261 <- shots/sh010/roll/v001/roll_rows.json (her_row_index read from the file)
  - assets/B01.mp4  <- color/v001/plates/B01.mp4 (graded, preferred)
                       else edit/v001/plates/B01.mp4 + PROVISIONAL band grade (colorist make_luts.band) for review only
                       else director lookdev/B01.png still (placeholder)
  - assets/ring_disp.png  shockwave refraction map (R=dx, G=dy, 128 = neutral)
  - compositions/mg2.html <- src/mg2.tpl.html + data
  - index.html (2160x3840, master time: mount host at data-start 9.72), proxy.html (540x960 review mount)
Usage: python3 tools/build.py   (re-run whenever roll_rows.json or a B01 plate updates)"""
import json, os, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MG2 = os.path.dirname(HERE)
PROJ = os.path.abspath(os.path.join(MG2, "../../../../.."))
SH = os.path.join(PROJ, "shots/sh010")
SCR = os.environ.get("MG2_SCRATCH", "/tmp/mg2_build")
os.makedirs(SCR, exist_ok=True)
cues = json.load(open(os.path.join(SH, "director/v001/cues.json")))
FPS = 25
F0, F1 = 243, 277                      # MG2 owns master f243..f276
assert cues["events"]["DROP"]["f"] == 261
PAL = cues["palette"]
info = {}

# ---------------- fonts ----------------
for f in os.listdir(os.path.join(SH, "director/v001/fonts")):
    shutil.copyfile(os.path.join(SH, "director/v001/fonts", f), os.path.join(MG2, "assets/fonts", f))

# ---------------- roll rows ----------------
rows_src = os.path.join(SH, "roll/v001/roll_rows.json")
rr = json.load(open(rows_src))
H = rr["her_row_index"]
col = rr["columns"]
font_px, cap = col["font_px"], col["cap_px"]
lx, rx = col["left_right_edge_x"], col["right_left_edge_x"]
win = rr["window"]
fitx = rr.get("fitted_cells_scaleX", {})
txt = {r["i"]: r for r in rr["row_text"]}
frames = {fr["f"]: fr for fr in rr["frames"]}
track = {}
for f in range(F0, 262):
    fr = frames.get(f) or frames[max(frames)]
    track[f] = next(r["y"] for r in fr["rows"] if r["i"] == H)
her_text = txt[H]["right"]
font = ImageFont.truetype(os.path.join(MG2, "assets/fonts/Montserrat-500.ttf"), font_px)
name_w = font.getlength(her_text) + len(her_text) * 0.02 * font_px - 0.02 * font_px   # same formula as MG1
stop_y = track[260]
fr261 = frames.get(261) or frames[max(frames)]
cards = []
for r in fr261["rows"]:
    y = r["y"]
    if y < win["top"] - 40 or y > win["bottom"] + 40:
        continue
    t = txt.get(r["i"])
    if not t:
        continue
    L, R = t["left"], t["right"]
    if r["i"] == H:
        R = ""                          # her cell becomes the hero name
    if not L and not R:
        continue
    # window feather at f261 (pushed 1.03 about her row: positions scaled about stop_y)
    yp = stop_y + (y - stop_y) * 1.03
    fe = win["feather"]
    a = min(1.0, max(0.0, (yp - win["top"]) / fe), max(0.0, (win["bottom"] - yp) / fe))
    cards.append(dict(i=r["i"], y=y, l=L, r=R, lsx=fitx.get(L, 1), rsx=fitx.get(R, 1), a=round(a, 3), her=r["i"] == H))
info["rows"] = f"roll_rows.json her_row_index={H} '{her_text}', {len(cards)} cards at f261, her y f261={track[261]}"

# ---------------- B01 plate ----------------
graded = os.path.join(SH, "color/v001/plates/B01.mp4")
ungraded = os.path.join(SH, "edit/v001/plates/B01.mp4")
out_plate = os.path.join(MG2, "assets/B01.mp4")

def nframes(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", p], capture_output=True, text=True)
    try: return int(r.stdout.strip().split(",")[0])
    except Exception: return 0

ENC = ["-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "25", "-an"]
if os.path.exists(graded) and nframes(graded) == 16:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", graded, "-vf", "scale=2400:900", *ENC, out_plate], check=True)
    info["B01"] = "color/v001/plates/B01.mp4 (GRADED, final)"
elif os.path.exists(ungraded) and nframes(ungraded) == 16:
    cube = os.path.join(SCR, "band.cube")
    if not os.path.exists(cube):
        subprocess.run([sys.executable, "-I", os.path.join(SH, "color/v001/make_luts.py"), SCR], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ungraded, "-vf", f"lut3d={cube},scale=2400:900", *ENC, out_plate], check=True)
    info["B01"] = "edit/v001/plates/B01.mp4 + PROVISIONAL band.cube (review only; swap to color/v001/plates/B01.mp4 by re-running build)"
else:
    still = os.path.join(SH, "director/v001/lookdev/B01.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", still, "-vf",
                    "scale=2400:900:force_original_aspect_ratio=increase,crop=2400:900", "-frames:v", "16", *ENC, out_plate], check=True)
    info["B01"] = "PLACEHOLDER still director/lookdev/B01.png"

# ---------------- shockwave refraction map ----------------
S = 512
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
dx, dy = (xx + 0.5) / S * 2 - 1, (yy + 0.5) / S * 2 - 1
rho = np.hypot(dx, dy) + 1e-6
RING, WID = 0.86, 0.07
z = (rho - RING) / WID
prof = z * np.exp(-z * z) * 2.3316                   # derivative-of-gaussian lens profile, peak |1|
prof[rho > 0.99] = 0
mx, my = prof * dx / rho, prof * dy / rho
img = np.stack([128 + 127 * mx, 128 + 127 * my, np.full_like(mx, 128)], -1)
Image.fromarray(np.clip(img, 0, 255).round().astype(np.uint8)).save(os.path.join(MG2, "assets/ring_disp.png"))

# ---------------- data + composition ----------------
DATA = dict(F0=F0, F1=F1, track={str(k): v for k, v in track.items()}, stop_y=stop_y, name_x=rx, name_w=round(name_w, 1),
            cap=cap, font_px=font_px, her_text=her_text, lx=lx, rx=rx, cards=cards, pal=PAL,
            ring_ratio=RING, beats=[b for b in cues["beats_f"] if F0 <= b < F1])
tpl = open(os.path.join(MG2, "src/mg2.tpl.html")).read()
html = tpl.replace("/*@@DATA@@*/{}", json.dumps(DATA, separators=(",", ":")))
html = html.replace("@@NAME@@", her_text)
html = html.replace("@@CARDS@@", "".join(
    f'<div class="mg2-card" id="mg2-c{c["i"]}"><span class="l"><span class="fit" style="transform:scaleX({c["lsx"]})'
    f';transform-origin:right center">{c["l"]}</span></span><span class="r"><span class="fit" style="transform:scaleX({c["rsx"]});'
    f'transform-origin:left center">{c["r"]}</span></span></div>' for c in cards))
open(os.path.join(MG2, "compositions/mg2.html"), "w").write(html)

HEAD = '<meta charset="UTF-8" />\n    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
index = f"""<!doctype html>
<html lang="en">
  <head>
    {HEAD}
    <meta name="viewport" content="width=2160, height=3840" />
    <style>html,body{{margin:0;width:2160px;height:3840px;overflow:hidden;background:transparent}}#root{{position:absolute;inset:0}}</style>
  </head>
  <body>
    <!-- MG2 SUPER ART FX on MASTER time: this root runs f0..f276 (11.08 s); the scene shows f243..f276. Transparent. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="11.08" data-fps="25" data-width="2160" data-height="3840">
      <div id="mg2" data-composition-id="mg2" data-composition-src="compositions/mg2.html" data-start="9.72" data-duration="1.36"
           data-track-index="1" data-track-kind="graphics" data-width="2160" data-height="3840"></div>
    </div>
    <script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
open(os.path.join(MG2, "index.html"), "w").write(index)
proxy = index.replace("2160px;height:3840px", "540px;height:960px").replace("width=2160, height=3840", "width=540, height=960")
proxy = proxy.replace('data-duration="11.08"', 'data-duration="1.36"').replace('data-width="2160" data-height="3840"', 'data-width="540" data-height="960"')
proxy = proxy.replace('data-start="9.72"', 'data-start="0"')
proxy = proxy.replace("<!-- MG2 SUPER ART FX on MASTER time: this root runs f0..f276 (11.08 s); the scene shows f243..f276. Transparent. -->",
                      "<!-- 540x960 REVIEW mount: local t0 = master f243. The scene fits its 2160x3840 stage to the host. -->")
open(os.path.join(MG2, "proxy.html"), "w").write(proxy)
json.dump(dict(info=info, name_w=name_w, stop_y=stop_y, cards=len(cards)), open(os.path.join(MG2, "check/build_info.json"), "w"), indent=1)
print(json.dumps(info, indent=1))
