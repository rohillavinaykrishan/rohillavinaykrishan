#!/usr/bin/env python3
"""MG4 title card (master f350-449) -> compositions/mg4_title.html, index.html (master-timed mount), proxy_540/index.html.
Timing = master frames from director/v001/cues.json; scene clips use LOCAL seconds (f - 350) / 25; host mounts at 14.00 s.
Geometry of the band/name is shared with MG3 (../mg3_band/geometry.json) so the f349 -> f350 cut is seamless.
"""
import json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.dirname(HERE)
PROJ = os.path.abspath(os.path.join(MG, "../../../../.."))
CUES = json.load(open(os.path.join(PROJ, "shots/sh010/director/v001/cues.json")))
GEO = json.load(open(os.path.join(os.path.dirname(MG), "mg3_band/geometry.json")))
FPS, P = CUES["fps"], CUES["palette"]
F0, F1 = 350, 450
DUR = (F1 - F0) / FPS
T = lambda f: round((f - F0) / FPS, 4)
TAN = math.tan(math.radians(12))
CX, CY = 1080, 1700

css_poly = lambda pts: "polygon(" + ",".join(f"{x:.1f}px {y:.1f}px" for x, y in pts) + ")"
svg_pts = lambda pts: " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
centre_y = lambda x: CY - (x - CX) * TAN            # the band's centre line (through the name centre)


def collapsed(pts):
    return [(x, centre_y(x)) for x, y in pts]


band, eu, ed = GEO["band_poly"], GEO["echo_up_poly"], GEO["echo_dn_poly"]
N = GEO["name"]
S1, S2 = N["l1"]["size_px"], N["l2"]["size_px"]
TOP1, TOP2 = N["l1"]["baseline_y"] - 0.9 * S1, N["l2"]["baseline_y"] - 0.9 * S2
blk_h = N["l1"]["cap_px"] + (N["l2"]["baseline_y"] - N["l1"]["baseline_y"])      # 570
# title setting: x0.8, block y 1500 -> 1956 (treatment: y 1500-1950)
NS = 0.8
NY = 1500 + blk_h * NS / 2 - CY                                                   # +28 px

# logo: canvas = 1618x862 logo + 60 px bloom pad; logo box y 700-1150 (450 px tall), centred x
LK = 450 / 862
LW, LH = 1738 * LK, 982 * LK
LX, LY = CX - LW / 2, 700 - 60 * LK
lean = 0.5 * (1220 - 600) * TAN


def wipe(x):   # -12 deg slash mask front at x (top leads)
    return f"polygon(0px 600px, {x + lean:.1f}px 600px, {x - lean:.1f}px 1220px, 0px 1220px)"


RULE_Y, L2_BL, L3_BL = 2030, 2190, 2300
EMB = [dict(id=1, f=392, n=54, x=430, dx=70, y0=2980, y1=2240, s=28),
       dict(id=2, f=404, n=60, x=1730, dx=-60, y0=3000, y1=2380, s=24),
       dict(id=3, f=417, n=60, x=1470, dx=45, y0=2960, y1=2560, s=20)]

js = []
eo, ei = "expoOut", "expoIn"
# collapse f350-355 (6 f, exit ease) onto the name line, then a 1-frame Ki White slash line on f356
cd = 6 / FPS
js.append(f'tl.to("#mg4-band-clip", {{clipPath: "{css_poly(collapsed(band))}", duration: {cd}, ease: {ei}}}, 0);')
js.append(f'tl.to("#mg4-eu-clip", {{clipPath: "{css_poly(collapsed(eu))}", duration: {cd}, ease: {ei}}}, 0);')
js.append(f'tl.to("#mg4-ed-clip", {{clipPath: "{css_poly(collapsed(ed))}", duration: {cd}, ease: {ei}}}, 0);')
for i in ("edge", "glow"):
    js.append(f'tl.to("#mg4-{i}", {{attr: {{points: "{svg_pts(collapsed(band))}"}}, duration: {cd}, ease: {ei}}}, 0);')
js.append(f'tl.set("#mg4-collapse", {{opacity: 0}}, {T(356)});')
js.append(f'tl.set("#mg4-slash", {{opacity: 1}}, {T(356)});')
js.append(f'tl.set("#mg4-slash", {{opacity: 0}}, {T(357)});')
# name: f356-367 (11 f) to the title setting, Ki glow 80% -> 40%
js.append(f'tl.to("#mg4-name", {{scale: {NS}, y: {NY:.1f}, duration: {11 / FPS}, ease: {eo}}}, {T(356)});')
js.append(f'tl.to("#mg4-name-glow", {{opacity: 0.4, duration: {11 / FPS}, ease: {eo}}}, {T(356)});')
# line-up rises in from below (11 f) + slow push 1.00 -> 1.04 to f449
js.append(f'tl.fromTo("#mg4-lineup-rise", {{y: 340, opacity: 0}}, {{y: 0, opacity: 1, duration: {11 / FPS}, ease: {eo}}}, 0);')
js.append(f'tl.fromTo("#mg4-lineup-push", {{scale: 1}}, {{scale: 1.04, duration: {(449 - 350) / FPS}, ease: "none"}}, 0);')
js.append(f'tl.fromTo("#mg4-smoke", {{x: -40}}, {{x: 60, duration: {DUR}, ease: "none"}}, 0);')
# logo lands f360: -12 deg slash mask wipe L->R over f354-360 (6 f, entrance ease)
js.append(f'tl.fromTo("#mg4-logo-wipe", {{clipPath: "{wipe(LX - 2 * lean)}", opacity: 0.0}}, '
          f'{{clipPath: "{wipe(LX + LW + 2 * lean)}", opacity: 1, duration: {6 / FPS}, ease: {eo}}}, {T(354)});')
# rule draws L->R f370-378
js.append(f'tl.fromTo("#mg4-rule", {{scaleX: 0}}, {{scaleX: 1, duration: {8 / FPS}, ease: {eo}}}, {T(370)});')
# lines on beats 380 / 392: rise 24 px + fade, 6 f
js.append(f'tl.fromTo("#mg4-l2", {{y: 24, opacity: 0}}, {{y: 0, opacity: 1, duration: {6 / FPS}, ease: {eo}}}, {T(380)});')
js.append(f'tl.fromTo("#mg4-l3", {{y: 24, opacity: 0}}, {{y: 0, opacity: 1, duration: {6 / FPS}, ease: {eo}}}, {T(392)});')
# embers
for e in EMB:
    d = min(e["n"], 449 - e["f"] + 1) / FPS
    js.append(f'tl.fromTo("#mg4-ember{e["id"]}", {{x: 0, y: 0}}, {{x: {e["dx"]}, y: {e["y1"] - e["y0"]}, duration: {e["n"] / FPS}, ease: "none"}}, {T(e["f"])});')
    js.append(f'tl.fromTo("#mg4-ember{e["id"]}", {{opacity: 0}}, {{opacity: 1, duration: {8 / FPS}, ease: "none"}}, {T(e["f"])});')
    if e["f"] + e["n"] <= 449:
        js.append(f'tl.to("#mg4-ember{e["id"]}", {{opacity: 0, duration: {14 / FPS}, ease: "none"}}, {T(e["f"] + e["n"] - 14)});')
js_body = "\n      ".join(js)

ember_html = "\n".join(
    f'      <div id="mg4-ember{e["id"]}" class="ember" style="left:{e["x"] - e["s"] / 2:.0f}px; top:{e["y0"] - e["s"] / 2:.0f}px; '
    f'width:{e["s"]}px; height:{e["s"]}px"></div>' for e in EMB)

scene = f"""<template>
  <style>
    @font-face {{ font-family: "BCI"; src: url("assets/fonts/BarlowCondensed-900Italic.ttf"); }}
    @font-face {{ font-family: "BC6"; src: url("assets/fonts/BarlowCondensed-600.ttf"); }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {P["aubergine_ink"]}; }}
    #root .layer {{ position: absolute; left: 0; top: 0; width: 2160px; height: 3840px; }}
    #mg4-bg {{ background: radial-gradient(ellipse 1500px 1300px at 1080px 1350px, {P["mulberry"]}b0 0%, {P["mulberry"]}40 45%, {P["aubergine_ink"]}00 75%), {P["aubergine_ink"]}; }}
    #mg4-lineup-push {{ transform-origin: 1080px 3840px; }}
    #mg4-lineup {{ position: absolute; left: 0; top: 2872px; width: 2160px; height: 968px; }}
    #mg4-lineup-fade {{ position: absolute; left: 0; top: 2840px; width: 2160px; height: 360px;
      background: linear-gradient({P["aubergine_ink"]} 0%, {P["aubergine_ink"]}00 100%); }}
    #mg4-smoke {{ background:
      radial-gradient(ellipse 900px 260px at 600px 2980px, {P["plum_mid"]}38 0%, {P["plum_mid"]}00 100%),
      radial-gradient(ellipse 1100px 300px at 1600px 3150px, {P["chalk"]}14 0%, {P["chalk"]}00 100%),
      radial-gradient(ellipse 800px 220px at 1100px 2860px, {P["saffron"]}12 0%, {P["saffron"]}00 100%); }}
    #mg4-eu-clip {{ clip-path: {css_poly(eu)}; }}
    #mg4-ed-clip {{ clip-path: {css_poly(ed)}; }}
    #mg4-band-clip {{ clip-path: {css_poly(band)}; }}
    #root .rot {{ position: absolute; width: 2400px; height: 900px; left: -120px; transform-origin: 1200px 450px; transform: rotate(-12deg); }}
    #root .rot img {{ position: absolute; left: 0; top: 0; width: 2400px; height: 900px; }}
    #root .echo img {{ opacity: 0.62; }}
    #mg4-logo-wipe {{ opacity: 0; clip-path: {wipe(LX - 2 * lean)}; }}
    #mg4-logo {{ position: absolute; left: {LX:.1f}px; top: {LY:.1f}px; width: {LW:.1f}px; height: {LH:.1f}px; }}
    #root .nm {{ position: absolute; left: 0; width: 2160px; text-align: center; font-family: "BCI"; line-height: 1;
      letter-spacing: 0.01em; padding-left: 0.01em; white-space: nowrap; }}
    #root .l1 {{ top: {TOP1:.1f}px; font-size: {S1}px; }}
    #root .l2 {{ top: {TOP2:.1f}px; font-size: {S2}px; }}
    #mg4-name {{ transform-origin: {CX}px {CY}px; }}
    #mg4-name-glow .nm {{ color: {P["saffron"]}; filter: blur(18px); }}
    #mg4-name-main .nm {{ color: {P["ki_white"]}; text-shadow: 0 18px 0 {P["mulberry"]}, 0 0 6px {P["saffron"]}99; }}
    #mg4-rule {{ position: absolute; left: {CX - 210}px; top: {RULE_Y}px; width: 420px; height: 8px; background: {P["saffron"]};
      transform-origin: 0 50%; box-shadow: 0 0 18px {P["saffron"]}88; }}
    #root .card {{ position: absolute; left: 0; width: 2160px; text-align: center; font-family: "BC6"; line-height: 1;
      letter-spacing: 0.30em; padding-left: 0.30em; white-space: nowrap; opacity: 0; }}
    #mg4-l2 {{ top: {L2_BL - 0.9 * 96:.1f}px; font-size: 96px; color: {P["ki_white"]}; }}
    #mg4-l3 {{ top: {L3_BL - 0.9 * 64:.1f}px; font-size: 64px; color: {P["chalk"]}; }}
    #root .ember {{ position: absolute; border-radius: 50%; opacity: 0;
      background: radial-gradient(circle, {P["ki_white"]} 0%, {P["saffron"]} 45%, {P["saffron"]}00 100%);
      box-shadow: 0 0 24px 8px {P["saffron"]}66; }}
  </style>
  <div id="root" data-composition-id="mg4_title" data-width="2160" data-height="3840" data-layout-allow-overflow data-layout-allow-overlap>
    <div id="mg4-bg" class="layer" style="z-index:0"></div>
    <!-- LINE-UP ART (tritone + saffron rim baked), bottom-anchored -->
    <div id="mg4-lineup-rise" class="layer" style="z-index:1">
      <div id="mg4-lineup-push" class="layer">
        <img id="mg4-lineup" src="assets/lineup.png" alt="">
        <div id="mg4-lineup-fade"></div>
        <div id="mg4-smoke" class="layer"></div>
      </div>
    </div>
    <!-- COLLAPSE f350-355: band (B08 last frame) + echo bands close onto the name line -->
    <div id="mg4-collapse" class="layer" style="z-index:2">
      <div id="mg4-eu-clip" class="layer echo"><div class="rot" style="top:{GEO['echo_up_poly'][0][1] - 255.1 + 130 - 450:.0f}px"><img src="assets/echo_u.jpg" alt=""></div></div>
      <div id="mg4-ed-clip" class="layer echo"><div class="rot" style="top:{GEO['echo_dn_poly'][0][1] - 255.1 + 130 - 450:.0f}px"><img src="assets/echo_d.jpg" alt=""></div></div>
      <div id="mg4-band-clip" class="layer"><div class="rot" style="top:{CY - 450}px"><img src="assets/band_B08.jpg" alt=""></div></div>
      <svg class="layer" viewBox="0 0 2160 3840" width="2160" height="3840" style="overflow:visible">
        <defs><filter id="mg4-blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="20"/></filter></defs>
        <polygon id="mg4-glow" points="{svg_pts(band)}" fill="none" stroke="{P["saffron"]}" stroke-width="40" opacity="0.5" filter="url(#mg4-blur)"/>
        <polygon id="mg4-edge" points="{svg_pts(band)}" fill="none" stroke="{P["saffron"]}" stroke-width="6"/>
      </svg>
    </div>
    <svg id="mg4-slash" class="layer" viewBox="0 0 2160 3840" width="2160" height="3840" style="z-index:3; opacity:0">
      <line x1="-60" y1="{centre_y(-60):.1f}" x2="2220" y2="{centre_y(2220):.1f}" stroke="{P["ki_white"]}" stroke-width="10"/>
    </svg>
    <!-- EMBERS -->
    <div class="layer" style="z-index:4">
{ember_html}
    </div>
    <!-- SF LOGO (gold-mapped, 6% bloom baked) lands f360 -->
    <div id="mg4-logo-wipe" class="layer" style="z-index:5"><img id="mg4-logo" src="assets/logo.png" alt="STREET FIGHTER"></div>
    <!-- NAME: band position at f350 -> title setting (x0.8, y 1500-1956) f356-367 -->
    <div id="mg4-name" class="layer" style="z-index:6">
      <div id="mg4-name-glow" class="layer" style="opacity:0.8"><div class="nm l1">SUKANYA</div><div class="nm l2">DILIP DHARIYA</div></div>
      <div id="mg4-name-main" class="layer"><div class="nm l1">SUKANYA</div><div class="nm l2">DILIP DHARIYA</div></div>
    </div>
    <div class="layer" style="z-index:7">
      <div id="mg4-rule"></div>
      <div id="mg4-l2" class="card">SR. MATCHMOVE ARTIST</div>
      <div id="mg4-l3" class="card">STREET FIGHTER&nbsp;&nbsp;&middot;&nbsp;&nbsp;DNEG</div>
    </div>
  </div>
  <script>
    (function () {{
      function bez(x1, y1, x2, y2) {{
        return function (t) {{
          if (t <= 0) return 0; if (t >= 1) return 1;
          let u = t;
          for (let i = 0; i < 12; i++) {{
            const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
            const x = ((ax * u + bx) * u + cx) * u - t;
            const dx = (3 * ax * u + 2 * bx) * u + cx;
            if (Math.abs(x) < 1e-6 || dx === 0) break;
            u = Math.min(1, Math.max(0, u - x / dx));
          }}
          const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
          return ((ay * u + by) * u + cy) * u;
        }};
      }}
      const expoOut = bez(0.16, 1, 0.3, 1), expoIn = bez(0.7, 0, 0.84, 0);
      const tl = gsap.timeline({{ paused: true }});
      {js_body}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["mg4_title"] = tl;
    }})();
  </script>
</template>
"""
open(os.path.join(MG, "compositions/mg4_title.html"), "w").write(scene)

GS = '<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'


def root(w, h, start, total, note, scale=None):
    wrap_o, wrap_c = ('<div id="proxy-scale">', '</div>') if scale else ("", "")
    css = ("#proxy-scale { position: absolute; left: 0; top: 0; width: 2160px; height: 3840px; transform: scale(%s); transform-origin: 0 0; }" % scale) if scale else ""
    return f"""<!doctype html>
<!-- {note} -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    {GS}
    <style>html, body {{ margin: 0; width: {w}px; height: {h}px; overflow: hidden; background: transparent; }} {css}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-fps="{FPS}" data-width="{w}" data-height="{h}">
      {wrap_o}<div id="mg4_title" data-composition-id="mg4_title" data-composition-src="compositions/mg4_title.html"
        data-start="{start}" data-duration="{DUR}" data-track-index="1" data-track-kind="graphics" data-width="2160" data-height="3840"></div>{wrap_c}
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""


open(os.path.join(MG, "index.html"), "w").write(root(2160, 3840, F0 / FPS, F1 / FPS, "MG4 title, MASTER-TIMED mount: scene host at master f350 = 14.00 s"))
os.makedirs(os.path.join(MG, "proxy_540"), exist_ok=True)
open(os.path.join(MG, "proxy_540/index.html"), "w").write(root(540, 960, 0, DUR, "MG4 540x960 REVIEW PROXY (scene x0.25), local t=0 = master f350", scale="0.25"))
print("wrote mg4")
