#!/usr/bin/env python3
"""Roll typesetter B: builds roll.html (HyperFrames sub-comp) + roll_rows.json.

Rows = rows_verified.txt (if present, the transcribed rows ABOVE SAMITH) + source/credits.txt.
Usage: python3 gen_roll.py   (run from anywhere)
All geometry in master 2160x3840 px, master frames at 25 fps (comp f0 = master f0).
"""
import json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "../../../.."))
cues = json.load(open(os.path.join(PROJ, "shots/sh010/director/v001/cues.json")))

FPS = cues["fps"]                      # 25
PITCH = cues["roll"]["row_pitch_4k"]   # 93
GUTTER_X = 1083
HALF_GAP = 63                          # measured: real gap 31 px @720 (x 345.5 | 376.5) x 4.05 / 2
V = cues["roll"]["scroll_4k_px_per_frame"]  # 19.0 px/frame
HER_PARK_Y = cues["roll"]["her_row_y_at_f243"]  # 1536 (parked y of her row's cap centre)
F_STOP0, F_STOP1 = 243, 252            # ease-to-stop window
DECEL_N = F_STOP1 - F_STOP0            # 9 frames
DECEL_D = V * DECEL_N / 2.0            # quad ease-out with v0 = 19 -> 85.5 px, C1-continuous
F_END = 261                            # roll hands over to MG2's shatter at f261
F_JSON_END = 272                       # json covers f0..272 (static after f252)
FONT_PX = 63                           # Montserrat cap 0.70 em -> cap 44 px
CAP = 44
TRACK = "0.02em"
WIN_TOP, WIN_BOT = 570, 3060           # roll window (header owns 470-560)
FEATHER = 48

def read_rows(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8").read().splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if not s:
            rows.append(None)  # letter gap
            continue
        l, _, r = s.partition("|")
        rows.append((l.strip(), r.strip()))
    return rows

pre = read_rows(os.path.join(HERE, "rows_verified.txt"))
# strip trailing blank-only noise but keep internal gaps; a trailing blank before SAMITH is a real gap only if written
while pre and pre[0] is None:
    pre.pop(0)
cred = read_rows(os.path.join(PROJ, "source/credits.txt"))
while cred and cred[-1] is None:
    cred.pop()
rows = pre + cred
her = next(i for i, r in enumerate(rows) if r and r[1] == "SUKANYA DILIP DHARIYA")

def offset(f):
    """distance (px) her row still has to travel up before parking, at master frame f (float ok)."""
    if f <= F_STOP0:
        return DECEL_D + V * (F_STOP0 - f)
    if f >= F_STOP1:
        return 0.0
    u = (f - F_STOP0) / DECEL_N
    return DECEL_D * (1 - u) ** 2

def row_y(i, f):
    return HER_PARK_Y + (i - her) * PITCH + offset(f)

# ---------- roll_rows.json ----------
frames = []
for f in range(0, F_JSON_END + 1):
    frames.append({"f": f, "rows": [{"i": i, "y": round(row_y(i, f), 2)} for i, r in enumerate(rows) if r]})
meta = {
    "frames": frames,
    "her_row_index": her,
    "pitch": PITCH,
    "gutter_x": GUTTER_X,
    "y_ref": "cap centre of the row (Montserrat 500, cap 44 px), master 2160x3840 px",
    "fps": FPS,
    "frame_base": "master frame numbers (roll comp starts at master f0)",
    "row_text": [{"i": i, "left": r[0], "right": r[1]} for i, r in enumerate(rows) if r],
    "blank_rows": [i for i, r in enumerate(rows) if r is None],
    "columns": {"left_right_edge_x": GUTTER_X - HALF_GAP, "right_left_edge_x": GUTTER_X + HALF_GAP,
                "font": "Montserrat 500", "font_px": FONT_PX, "cap_px": CAP, "tracking": TRACK},
    "window": {"top": WIN_TOP, "bottom": WIN_BOT, "feather": FEATHER},
    "motion": {"speed_px_per_frame": V, "ease_to_stop": [F_STOP0, F_STOP1], "ease": "quad ease-out (power1.out), v continuous",
               "decel_distance_px": DECEL_D, "her_y_at_f243": round(row_y(her, 243), 2), "her_y_parked": HER_PARK_Y,
               "roll_visible_until_f": F_END - 1},
    "dimming": {"others": [[200, 1.0], [232, 0.6], [243, 0.6], [252, 0.22]], "others_colour": "Ki White -> Chalk f200-232",
                "her_row": "both cells 100% to f243; left cell then dims with others; right cell Ki White -> Saffron f243-249 (expo-out), stays 100%"},
    "source_rows": {"verified_prepended": len(pre), "credits_txt": len(cred)},
}
json.dump(meta, open(os.path.join(HERE, "roll_rows.json"), "w"), separators=(",", ":"))

# ---------- roll.html ----------
# Each row div: height = PITCH, line-height = PITCH; Montserrat hhea asc 968 / desc 251 (/1000).
# baseline from div top = (PITCH - 1.219*fs)/2 + 0.968*fs ; cap centre = baseline - 0.35*fs
cap_centre_in_div = (PITCH - 1.219 * FONT_PX) / 2 + 0.968 * FONT_PX - 0.35 * FONT_PX
# strip origin: row i top = i*PITCH; at strip translateY = T, row i cap centre = T + i*PITCH + cap_centre_in_div
def strip_T(f):
    return row_y(0, f) - cap_centre_in_div

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

row_html = []
for i, r in enumerate(rows):
    top = i * PITCH
    if r is None:
        continue
    cls = "rr her" if i == her else "rr"
    row_html.append(
        f'<div class="{cls}" id="rr-{i}" style="top:{top}px">'
        f'<span class="l{" herl" if i == her else " dim"}">{esc(r[0])}</span>'
        f'<span class="r{" hername" if i == her else " dim"}">{esc(r[1])}</span></div>')

s = lambda f: round(f / FPS, 6)
html = f"""<template>
  <!-- Roll typesetter B, sh010 roll v001. Generated by gen_roll.py: edit the generator, not this file.
       Master frame numbers: this comp's t=0 is master f0 (mount with data-start="0"). 25 fps.
       Linear 19 px/f to f243, quad ease-out to a stop at f252 with SUKANYA DILIP DHARIYA's cap centre at y {HER_PARK_Y}.
       Visible f0-f260; MG2's shatter takes the rows over at f261 (roll_rows.json). -->
  <style>
    @font-face {{ font-family: "Montserrat Roll"; font-weight: 500; src: url("assets/fonts/Montserrat-500.ttf") format("truetype"); }}
    #root {{ position: absolute; inset: 0; background: transparent; overflow: hidden; }}
    #roll-win {{ position: absolute; left: 0; top: {WIN_TOP}px; width: 2160px; height: {WIN_BOT - WIN_TOP}px; overflow: hidden;
      -webkit-mask-image: linear-gradient(to bottom, transparent 0, #000 {FEATHER}px, #000 calc(100% - {FEATHER}px), transparent 100%);
      mask-image: linear-gradient(to bottom, transparent 0, #000 {FEATHER}px, #000 calc(100% - {FEATHER}px), transparent 100%); }}
    #roll-strip {{ position: absolute; left: 0; top: -{WIN_TOP}px; width: 2160px; height: {len(rows) * PITCH}px; will-change: transform; }}
    .rr {{ position: absolute; left: 0; width: 2160px; height: {PITCH}px; line-height: {PITCH}px;
      font-family: "Montserrat Roll", Montserrat, sans-serif; font-weight: 500; font-size: {FONT_PX}px;
      letter-spacing: {TRACK}; text-transform: uppercase; white-space: nowrap; font-kerning: normal; }}
    .rr span {{ position: absolute; top: 0; color: var(--ki-white, #FFF3DC); }}
    .rr .l {{ right: {2160 - (GUTTER_X - HALF_GAP)}px; text-align: right; }}
    .rr .r {{ left: {GUTTER_X + HALF_GAP}px; text-align: left; }}
  </style>
  <div id="root" data-composition-id="roll" data-width="2160" data-height="3840">
    <div id="roll-clip" class="clip" data-start="0" data-duration="{s(F_END)}" data-track-index="1" data-layout-allow-overflow style="position:absolute;inset:0">
      <div id="roll-win">
        <div id="roll-strip">
          {chr(10).join('          ' + h for h in row_html).lstrip()}
        </div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const F = (f) => f / {FPS};
      // scroll: linear 19 px/f f0-243, then quad ease-out (power1.out, velocity-continuous) f243-252, park
      tl.fromTo("#roll-strip", {{ y: {round(strip_T(0), 3)} }}, {{ y: {round(strip_T(F_STOP0), 3)}, duration: F({F_STOP0}), ease: "none" }}, 0);
      tl.to("#roll-strip", {{ y: {round(strip_T(F_STOP1), 3)}, duration: F({DECEL_N}), ease: "power1.out" }}, F({F_STOP0}));
      // dimming: others 100% -> 60% (Ki White -> Chalk) f200-232 linear; -> 22% f243-252 expo-out
      tl.fromTo("#roll-strip .dim", {{ opacity: 1, color: "#FFF3DC" }}, {{ opacity: 0.6, color: "#D9CFC3", duration: F(32), ease: "none" }}, F(200));
      tl.fromTo("#roll-strip .herl", {{ color: "#FFF3DC" }}, {{ color: "#D9CFC3", duration: F(32), ease: "none" }}, F(200));
      tl.to("#roll-strip .dim", {{ opacity: 0.22, duration: F(9), ease: "expo.out" }}, F({F_STOP0}));
      tl.fromTo("#roll-strip .herl", {{ opacity: 1 }}, {{ opacity: 0.22, duration: F(9), ease: "expo.out" }}, F({F_STOP0}));
      // her name (right cell) Ki White -> Saffron, 6 f expo-out from f243
      tl.fromTo("#roll-strip .hername", {{ color: "#FFF3DC" }}, {{ color: "#FFB12A", duration: F(6), ease: "expo.out" }}, F({F_STOP0}));
      tl.set({{}}, {{}}, F({F_END}));
      window.__timelines["roll"] = tl;
    }})();
  </script>
</template>
"""
open(os.path.join(HERE, "roll.html"), "w").write(html)

index = f"""<!doctype html>
<html>
  <head><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script></head>
  <body style="margin:0;background:#14080F">
    <!-- Review harness only: mounts roll.html at master f0 over Aubergine. The comp lead mounts roll.html directly. -->
    <div id="main" data-composition-id="main" data-start="0" data-duration="{s(F_JSON_END + 1)}" data-width="2160" data-height="3840">
      <div id="bg" style="position:absolute;inset:0;background:#14080F"></div>
      <div id="roll" data-composition-id="roll" data-composition-src="compositions/roll.html" data-start="0" data-duration="{s(F_END)}"
           data-track-index="1" data-track-kind="graphics" data-width="2160" data-height="3840" style="z-index:2"></div>
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
PREV = os.path.join(HERE, "preview")
os.makedirs(os.path.join(PREV, "compositions"), exist_ok=True)
os.makedirs(os.path.join(PREV, "assets/fonts"), exist_ok=True)
open(os.path.join(PREV, "index.html"), "w").write(index)
open(os.path.join(PREV, "compositions/roll.html"), "w").write(html)
import shutil
shutil.copy(os.path.join(PROJ, "shots/sh010/director/v001/fonts/Montserrat-500.ttf"), os.path.join(PREV, "assets/fonts/Montserrat-500.ttf"))
print(f"rows={len(rows)} (pre {len(pre)}, credits {len(cred)}) her={her} her_y@f0={row_y(her,0):.1f} her_y@f243={row_y(her,243):.1f}"
      f" top row y@f0={row_y(0,0):.1f} cap_centre_in_div={cap_centre_in_div:.2f}")
