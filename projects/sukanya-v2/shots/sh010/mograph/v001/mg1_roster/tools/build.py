"""MG1 build: (re)generates the HyperFrames project from upstream files.
  - compositions/roll.html  <- shots/sh010/roll/v001/roll.html (verbatim) or the MG1 placeholder roll
  - her-row track            <- shots/sh010/roll/v001/roll_rows.json (her_row_index, y = cap centre) or a model
  - compositions/mg1.html   <- src/mg1.tpl.html + panel markup + data (cues.json timing)
  - index.html (2160x3840 mount, for the comp lead) and proxy.html (540x960 mount, for the review proxy)
Run tools/sync_inputs.py first for the plates.  Usage: python3 tools/build.py"""
import json, os, shutil
import numpy as np
from PIL import Image, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MG1 = os.path.dirname(HERE)
PROJ = os.path.abspath(os.path.join(MG1, "../../../../.."))
SH = os.path.join(PROJ, "shots/sh010")
cues = json.load(open(os.path.join(SH, "director/v001/cues.json")))
FPS, N = 25, 261            # MG1 = master f0..f260
DUR = N / FPS               # 10.44 s
shots = {s["id"]: s for s in cues["shots"]}
assert cues["events"]["DROP"]["f"] == 261

# ---------------- roll + her-row track ----------------
roll_src = os.path.join(SH, "roll/v001/roll.html")
rows_src = os.path.join(SH, "roll/v001/roll_rows.json")
info = {}
if os.path.exists(rows_src):
    rr = json.load(open(rows_src))
    H = rr["her_row_index"]
    track = []
    for f in range(N):
        fr = rr["frames"][f]
        assert fr["f"] == f
        track.append(next(r["y"] for r in fr["rows"] if r["i"] == H))
    col = rr.get("columns", {})
    font_px = col.get("font_px", 63); cap = col.get("cap_px", 44); name_x = col.get("right_left_edge_x", 1142)
    her_text = next(r["right"] for r in rr["row_text"] if r["i"] == H)
    info["track"] = "roll_rows.json"
else:
    # model: 19 px/f, quad ease-out f243-252 to a stop at y 1536 (decel distance 85.5 px)
    track = []
    for f in range(N):
        if f <= 243: y = 1621.5 + 19 * (243 - f)
        elif f <= 252: u = (f - 243) / 9; y = 1621.5 - 85.5 * (1 - (1 - u) ** 2)
        else: y = 1536.0
        track.append(y)
    font_px, cap, name_x, her_text, H = 63, 44, 1142, "SUKANYA DILIP DHARIYA", 29
    info["track"] = "MG1 model (roll_rows.json missing)"

font = ImageFont.truetype(os.path.join(MG1, "assets/fonts/Montserrat-500.ttf"), font_px)
name_w = font.getlength(her_text) + len(her_text) * 0.02 * font_px - 0.02 * font_px

os.makedirs(os.path.join(MG1, "compositions"), exist_ok=True)
if os.path.exists(roll_src):
    shutil.copyfile(roll_src, os.path.join(MG1, "compositions/roll.html"))
    info["roll"] = "shots/sh010/roll/v001/roll.html (verbatim copy)"
else:
    lines = [l.strip() for l in open(os.path.join(PROJ, "source/credits.txt")) if l.strip()]
    rows = []
    for i, l in enumerate(lines):
        a, b = [x.strip() for x in l.split("|")]
        rows.append(f'<div class="rollph-row" style="top:{i * 93}px"><span class="rollph-l">{a}</span><span class="rollph-r">{b}</span></div>')
    t = open(os.path.join(MG1, "src/roll_placeholder.tpl.html")).read()
    t = t.replace("/*@@ROWS@@*/", "\n".join(rows)).replace("/*@@TRACK@@*/[]", json.dumps(track)).replace("/*@@HER@@*/0", str(H))
    open(os.path.join(MG1, "compositions/roll.html"), "w").write(t)
    info["roll"] = "MG1 placeholder roll"

# ---------------- grain tile ----------------
gp = os.path.join(MG1, "assets/grain_512.png")
if not os.path.exists(gp):
    rng = np.random.default_rng(7)
    g = np.clip(128 + rng.normal(0, 46, (512, 512)), 0, 255).astype(np.uint8)
    Image.fromarray(g, "L").save(gp)

# ---------------- panels ----------------
def fi(sid): return shots[sid]["f_in"]
def fo(sid): return shots[sid]["f_out"]

TAN = np.tan(np.radians(12))
def cover(pw, ph, h):  # counter-skewed plate box covering the visible parallelogram (x 0..2160)
    need_h = h + 2160 * TAN + 8
    s = max(2168 / pw, need_h / ph)
    return round(pw * s), round(ph * s)

# visits: o = open frame, c = close frame, open/close wipe lengths (frames), edge = saffron slash edge
P1 = dict(id="mg1-p1", cy=1300, h=1180, op=0.60, drift=1, plate=(2160, 1180), visits=[
    dict(o=0, c=105, open=0, close=3, shots=["A01", "A02", "A03"]),
    dict(o=126, c=147, open=6, close=3, shots=["A05"]),
    dict(o=168, c=188, open=6, close=3, shots=["A07"]),
    dict(o=209, c=219, open=6, close=2, shots=["A09"]),
    dict(o=224, c=232, open=2, close=2, edge=1, shots=["A11"]),
    dict(o=238, c=243, open=2, close=4, edge=1, closeDy=450, shots=["A13"]),
])
P2 = dict(id="mg1-p2", cy=2500, h=1180, op=0.60, drift=1, plate=(2160, 1180), visits=[
    dict(o=63, c=84, open=6, close=3, shots=["A02tail"]),
    dict(o=105, c=126, open=6, close=3, shots=["A04"]),
    dict(o=147, c=168, open=6, close=3, shots=["A06"]),
    dict(o=188, c=209, open=6, close=3, shots=["A08"]),
    dict(o=219, c=224, open=2, close=2, edge=1, shots=["A10"]),
    dict(o=232, c=238, open=2, close=2, edge=1, shots=["A12"]),
])
BAND = dict(id="mg1-band", cy=1750, h=900, op=0.92, drift=0, plate=(2400, 900), visits=[
    dict(o=243, c=N, open=6, close=1, shots=["C00"]),
])
# shot windows: A02's tail rides in P2 from f63 (same plate, media offset 21 f)
def shot_win(name):
    if name == "A02tail": return "A02", 63, 84, (63 - fi("A02")) / FPS
    return name, fi(name), min(fo(name), N), 0.0

panels_html, panels_data = [], []
for p in (P1, P2, BAND):
    w, h = cover(*p["plate"], p["h"])
    vids, pv = [], []
    for v in p["visits"]:
        sl = []
        for name in v["shots"]:
            sid, a, b, ms = shot_win(name)
            vid = f'{p["id"]}-{name}'.lower()
            attrs = f'data-media-start="{ms:.2f}" ' if ms else ""
            vids.append(f'<video id="{vid}" class="clip" src="assets/plates/{sid}.mp4" data-start="{a / FPS:.2f}" '
                        f'data-duration="{(b - a) / FPS:.2f}" {attrs}data-track-index="2" muted playsinline></video>')
            sl.append(dict(vid=vid, fin=a, fout=b))
        pv.append(dict(o=v["o"], c=v["c"], open=v["open"], close=v["close"], edge=v.get("edge", 0),
                       closeDy=v.get("closeDy", 0), shots=sl))
    panels_data.append(dict(id=p["id"], cy=p["cy"], h=p["h"], visits=pv, drift=p["drift"]))
    panels_html.append(
        f'<div id="{p["id"]}-pos" class="mg1-pos" style="top:{p["cy"] - p["h"] / 2:.0f}px;height:{p["h"]}px">'
        f'<div id="{p["id"]}-skew" class="mg1-skew" style="height:{p["h"]}px;opacity:{p["op"]}">'
        f'<div class="mg1-cs" style="width:{w}px;height:{h}px;transform:translate(-50%,-50%) skewY(12deg)">'
        + "".join(vids) +
        f'</div><div id="{p["id"]}-e1" class="mg1-edge"></div><div id="{p["id"]}-e2" class="mg1-edge"></div></div></div>')

DATA = dict(frames=N, drift=0.6 * 19.0, track=[round(y, 2) for y in track], name_x=name_x, name_w=round(name_w, 1),
            cap=cap, font_px=font_px, stop_y=track[-1], charge_fx=True,
            dim_in_mg1=not os.path.exists(roll_src),   # the real roll.html dims itself + turns her name Saffron
            panels=panels_data)

t = open(os.path.join(MG1, "src/mg1.tpl.html")).read()
t = t.replace("/*@@PANELS@@*/", "\n".join(panels_html)).replace("/*@@DATA@@*/{}", json.dumps(DATA, separators=(",", ":")))
open(os.path.join(MG1, "compositions/mg1.html"), "w").write(t)

GSAP = '<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
def root(w, h, comment):
    return f"""<!doctype html>
<html>
  <head>{GSAP}</head>
  <body style="margin:0;background:#14080F">
    <!-- {comment} -->
    <div id="main" data-composition-id="main" data-start="0" data-duration="{DUR:.2f}" data-width="{w}" data-height="{h}" data-fps="25">
      <div id="mg1" data-composition-id="mg1" data-composition-src="compositions/mg1.html" data-start="0" data-duration="{DUR:.2f}"
           data-track-index="1" data-track-kind="graphics" data-width="{w}" data-height="{h}" style="z-index:1"></div>
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
open(os.path.join(MG1, "index.html"), "w").write(root(2160, 3840, "MG1 mount at master scale (2160x3840). Comp lead: mount compositions/mg1.html at data-start=0, data-duration=10.44."))
PX = os.path.join(os.path.dirname(MG1), "mg1_proxy540")   # separate HyperFrames project (one root per project)
os.makedirs(PX, exist_ok=True)
for d in ("assets", "compositions"):
    l = os.path.join(PX, d)
    if not os.path.islink(l): os.symlink(os.path.join("..", "mg1_roster", d), l)
open(os.path.join(PX, "index.html"), "w").write(root(540, 960, "MG1 review proxy mount (540x960): same mg1_roster composition (symlinked), stage scaled to fit."))
info.update(name_x=name_x, name_w=round(name_w, 1), font_px=font_px, her_y_f200=track[200], her_y_f260=track[-1])
print(json.dumps(info, indent=1))
