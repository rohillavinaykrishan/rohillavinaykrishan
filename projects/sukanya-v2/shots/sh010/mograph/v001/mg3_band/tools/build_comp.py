#!/usr/bin/env python3
"""MG3 band chain (master f261-349) -> writes compositions/mg3_band.html, index.html, proxy.html.
All timing comes from director/v001/cues.json (master frame numbers). Re-run after cues change.
Clip times inside the scene are LOCAL seconds = (master_frame - 261) / 25; the host mounts at 10.44 s.
"""
import json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
MG = os.path.dirname(HERE)
PROJ = os.path.abspath(os.path.join(MG, "../../../../.."))
CUES = json.load(open(os.path.join(PROJ, "shots/sh010/director/v001/cues.json")))
FPS = CUES["fps"]
F0, F1 = 261, 350                       # owned master range [261, 350)
DUR = (F1 - F0) / FPS                   # 3.56 s
P = CUES["palette"]
B = [s for s in CUES["shots"] if s["layer"] == "super_band"]
CUTS = [s["f_in"] for s in B[1:]]        # 277 289 300 310 320 330 340
POPS = {"B02": dict(f=279, n=8, s=1.16, ty=-40), "B03": dict(f=290, n=8, s=1.30, ty=-70)}

T = lambda f: round((f - F0) / FPS, 4)

# ---- geometry (4K px) ----
CX, CY, BW, BH = 1080, 1700, 2400, 900
TAN = math.tan(math.radians(12))


def para(cx, cy, w, h):
    """-12 deg slash parallelogram (vertical sides, edges rising left->right) as CSS/SVG points."""
    x0, x1 = cx - w / 2, cx + w / 2
    r = (w / 2) * TAN
    return [(x0, cy - h / 2 + r), (x1, cy - h / 2 - r), (x1, cy + h / 2 - r), (x0, cy + h / 2 + r)]


band_pts = para(CX, CY, BW, BH)
ECHO_H, ECHO_GAP = 260, 120
eu_cy = CY - BH / 2 - ECHO_GAP - ECHO_H / 2      # 1000
ed_cy = CY + BH / 2 + ECHO_GAP + ECHO_H / 2      # 2400
eu_pts, ed_pts = para(CX, eu_cy, BW, ECHO_H), para(CX, ed_cy, BW, ECHO_H)
css_poly = lambda pts: "polygon(" + ",".join(f"{x:.1f}px {y:.1f}px" for x, y in pts) + ")"
svg_pts = lambda pts: " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

# name (spec section 6): SUKANYA cap 300 / DILIP DHARIYA cap 220, Barlow Condensed 900 Italic (cap = 0.70 em),
# baseline pitch 0.86 x line-2 em, block (cap top line 1 -> baseline line 2) centred on y 1700.
S1, S2 = round(300 / 0.70), round(220 / 0.70)   # 429, 314 px
PITCH = round(0.86 * S2)                          # 270
blk_top = CY - (300 + PITCH) / 2                  # 1415
BL1, BL2 = blk_top + 300, blk_top + 300 + PITCH  # baselines 1715, 1985
TOP1, TOP2 = BL1 - 0.9 * S1, BL2 - 0.9 * S2      # line-height:1 -> baseline sits 0.9 em below the box top

vids = "\n".join(
    f'        <video id="mg3-{s["id"]}" class="clip plate" muted playsinline src="assets/plates/{s["id"]}.mp4" '
    f'data-start="{T(s["f_in"])}" data-duration="{T(s["f_out"]) - T(s["f_in"]):.4f}" data-track-index="2"></video>'
    f'  <!-- master f{s["f_in"]}-{s["f_out"]-1} -->'
    for s in B)
# echo bands: during shot k they show shot k-1's afterimage (tritone still of its last frame)
echo_imgs = []
for k in range(1, len(B)):
    prev, cur = B[k - 1], B[k]
    for side in ("u", "d"):
        echo_imgs.append(
            f'        <img id="mg3-e{side}-{prev["id"]}" class="clip echo-img echo-{side}" src="assets/echo/{prev["id"]}{"" if side == "u" else "_mid"}.jpg" '
            f'data-start="{T(cur["f_in"])}" data-duration="{T(cur["f_out"]) - T(cur["f_in"]):.4f}" data-track-index="1" alt="">')
eu_imgs = "\n".join(e for e in echo_imgs if "echo-u" in e)
ed_imgs = "\n".join(e for e in echo_imgs if "echo-d" in e)
pop_imgs = []
for sid, p in POPS.items():
    for i in range(p["n"]):
        pop_imgs.append(f'          <img id="mg3-pop-{sid}-{i}" class="clip pop-img" src="assets/pop/{sid}_{i}.png" '
                        f'data-start="{T(p["f"] + i)}" data-duration="{1 / FPS:.4f}" data-track-index="4" alt="">')
pop_html = "\n".join(pop_imgs)

# ---------------- timeline (GSAP) ----------------
js = []
E_OUT = "expoOut"; E_IN = "expoIn"
# band slam, f261-264 (MG3 owns the band from the drop): per-frame keys, 3% overshoot (-72 px) on f263
for f, x in [(262, 160), (263, -72), (264, 0)]:   # f261 = 1150 is set immediately (gsap.set) below
    js.append(f'tl.set("#mg3-slam", {{x: {x}}}, {T(f)});')
# border flash + name nudge + rim pulse on every cut
nx, ny = 3 * math.cos(math.radians(12)), -3 * math.sin(math.radians(12))
for c in CUTS:
    js.append(f'tl.set("#mg3-edge", {{attr: {{stroke: "{P["ki_white"]}", "stroke-width": 16}}}}, {T(c)});')
    js.append(f'tl.set("#mg3-glow", {{opacity: 1}}, {T(c)});')
    js.append(f'tl.set("#mg3-edge", {{attr: {{stroke: "{P["saffron"]}", "stroke-width": 11}}}}, {T(c + 1)});')
    js.append(f'tl.set("#mg3-glow", {{opacity: 0.75}}, {T(c + 1)});')
    js.append(f'tl.set("#mg3-edge", {{attr: {{"stroke-width": 6}}}}, {T(c + 2)});')
    js.append(f'tl.set("#mg3-glow", {{opacity: 0.5}}, {T(c + 2)});')
    for i, k in enumerate((1.0, 0.66, 0.33, 0.0)):
        js.append(f'tl.set("#mg3-name", {{x: {nx * k:.2f}, y: {ny * k:.2f}}}, {T(c + i)});')
    js.append(f'tl.fromTo("#mg3-name-glow", {{opacity: 0.88}}, {{opacity: 0.80, duration: {6 / FPS}, ease: {E_OUT}{"" if c == CUTS[0] else ", immediateRender: false"}}}, {T(c)});')
# echo bands: slash-wipe in f277-283 (expo-out), drift along the -12 deg axis at 0.35x (14 px/frame)
for side, sign in (("u", -1), ("d", 1)):
    js.append(f'tl.fromTo("#mg3-echo-{side}-wipe", {{clipPath: "inset(0px 100% 0px 0px)"}}, '
              f'{{clipPath: "inset(0px 0% 0px 0px)", duration: {6 / FPS}, ease: {E_OUT}}}, {T(277)});')
for k in range(1, len(B)):
    prev, cur = B[k - 1], B[k]
    n = cur["f_out"] - cur["f_in"]
    for side, sign in (("u", -1), ("d", 1)):
        d = 14 * n / 2
        js.append(f'tl.fromTo("#mg3-e{side}-{prev["id"]}", {{x: {-sign * d:.0f}}}, {{x: {sign * d:.0f}, duration: {n / FPS}, ease: "none"}}, {T(cur["f_in"])});')
# SUPER ART tag: in f266 (6 f expo-out along the -12 deg axis), out by f300 (4 f expo-in)
ax, ay = math.cos(math.radians(12)), -math.sin(math.radians(12))
js.append(f'tl.fromTo("#mg3-tag", {{x: {-420 * ax:.1f}, y: {-420 * ay:.1f}, opacity: 0}}, '
          f'{{x: 0, y: 0, opacity: 1, duration: {6 / FPS}, ease: {E_OUT}}}, {T(266)});')
js.append(f'tl.to("#mg3-tag", {{x: {-420 * ax:.1f}, y: {-420 * ay:.1f}, opacity: 0, duration: {4 / FPS}, ease: {E_IN}}}, {T(296)});')
# roto pop-outs: break out of the band's top edge, 2 f in (expo-out), hold, 2 f back (expo-in)
for sid, p in POPS.items():
    a, b = p["f"], p["f"] + p["n"]
    js.append(f'tl.fromTo("#mg3-pop-{sid}", {{scale: 1, y: 0}}, {{scale: {p["s"]}, y: {p["ty"]}, duration: {2 / FPS}, ease: {E_OUT}}}, {T(a)});')
    js.append(f'tl.to("#mg3-pop-{sid}", {{scale: 1, y: 0, duration: {2 / FPS}, ease: {E_IN}}}, {T(b - 2)});')
js_body = "\n      ".join(js)

scene = f"""<template>
  <style>
    @font-face {{ font-family: "BCI"; src: url("assets/fonts/BarlowCondensed-900Italic.ttf"); }}
    @font-face {{ font-family: "CP"; src: url("assets/fonts/ChakraPetch-600.ttf"); }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: transparent; }}
    #root .layer {{ position: absolute; left: 0; top: 0; width: 2160px; height: 3840px; }}
    /* echo bands: tritone afterimage of the outgoing shot */
    #mg3-echo-u-clip {{ clip-path: {css_poly(eu_pts)}; }}
    #mg3-echo-d-clip {{ clip-path: {css_poly(ed_pts)}; }}
    #root .echo-rot {{ position: absolute; width: 2400px; height: 900px; left: -120px; transform-origin: 1200px 450px; transform: rotate(-12deg); }}
    #root .echo-img {{ position: absolute; left: 0; top: 0; width: 2400px; height: 900px; opacity: 0.62; }}
    /* band */
    #mg3-band-clip {{ clip-path: {css_poly(band_pts)}; }}
    #mg3-band-rot {{ position: absolute; left: {CX - BW / 2:.0f}px; top: {CY - BH / 2:.0f}px; width: {BW}px; height: {BH}px;
      transform-origin: 50% 50%; transform: rotate(-12deg); }}
    #root .plate {{ position: absolute; left: 0; top: 0; width: {BW}px; height: {BH}px; object-fit: cover; }}
    #mg3-pop-rot {{ position: absolute; left: {CX - BW / 2:.0f}px; top: {CY - BH / 2:.0f}px; width: {BW}px; height: {BH}px;
      transform-origin: 50% 50%; transform: rotate(-12deg); }}
    #root .pop {{ position: absolute; inset: 0; transform-origin: 50% 100%; filter: drop-shadow(0 22px 0 {P["mulberry"]}cc); }}
    #root .pop-img {{ position: absolute; left: 0; top: 0; width: {BW}px; height: {BH}px; }}
    /* SUPER ART HUD chip */
    #mg3-tag {{ opacity: 0; position: absolute; left: 150px; top: 2380px; padding: 12px 18px 10px 22px; background: {P["ki_white"]};
      color: {P["aubergine_ink"]}; font: 600 34px/1 "CP"; letter-spacing: 0.12em; white-space: nowrap; }}
    /* hero name (settled state of MG2's Super Art; MG3 carries it f277-349) */
    #root .nm {{ position: absolute; left: 0; width: 2160px; text-align: center; font-family: "BCI"; line-height: 1;
      letter-spacing: 0.01em; padding-left: 0.01em; white-space: nowrap; }}
    #root .l1 {{ top: {TOP1:.1f}px; font-size: {S1}px; }}
    #root .l2 {{ top: {TOP2:.1f}px; font-size: {S2}px; }}
    #mg3-name-glow .nm {{ color: {P["saffron"]}; filter: blur(18px); }}
    #mg3-name-main .nm {{ color: {P["ki_white"]}; text-shadow: 0 18px 0 {P["mulberry"]}, 0 0 6px {P["saffron"]}99; }}
  </style>
  <div id="root" data-composition-id="mg3_band" data-width="2160" data-height="3840" data-layout-allow-overflow data-layout-allow-overlap>
    <!-- ECHO BANDS (f277-349) -->
    <div id="mg3-echo-u-clip" class="layer" style="z-index:1">
      <div id="mg3-echo-u-wipe" class="layer">
        <div class="echo-rot" style="top:{eu_cy - 450:.0f}px">
{eu_imgs}
        </div>
      </div>
    </div>
    <div id="mg3-echo-d-clip" class="layer" style="z-index:1">
      <div id="mg3-echo-d-wipe" class="layer">
        <div class="echo-rot" style="top:{ed_cy - 450:.0f}px">
{ed_imgs}
        </div>
      </div>
    </div>
    <svg id="mg3-echo-lines" class="layer" style="z-index:1" viewBox="0 0 2160 3840" width="2160" height="3840">
      <g id="mg3-echo-edges" fill="none" stroke="{P["saffron"]}" stroke-width="3" opacity="0.35">
        <polygon points="{svg_pts(eu_pts)}"/><polygon points="{svg_pts(ed_pts)}"/>
      </g>
    </svg>
    <!-- BAND: plates B01-B08 (UNLOCK grade baked), border, roto pop-outs -->
    <div id="mg3-slam" class="layer" style="z-index:2">
      <div id="mg3-band-clip" class="layer">
        <div id="mg3-band-rot">
{vids}
        </div>
      </div>
      <svg class="layer" viewBox="0 0 2160 3840" width="2160" height="3840" style="overflow:visible">
        <defs><filter id="mg3-blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="20"/></filter></defs>
        <polygon id="mg3-glow" points="{svg_pts(band_pts)}" fill="none" stroke="{P["saffron"]}" stroke-width="40" opacity="0.5" filter="url(#mg3-blur)"/>
        <polygon id="mg3-edge" points="{svg_pts(band_pts)}" fill="none" stroke="{P["saffron"]}" stroke-width="6"/>
      </svg>
      <div id="mg3-pop-rot">
        <div id="mg3-pop-B02" class="pop">
{chr(10).join(x for x in pop_imgs if "B02" in x)}
        </div>
        <div id="mg3-pop-B03" class="pop">
{chr(10).join(x for x in pop_imgs if "B03" in x)}
        </div>
      </div>
    </div>
    <!-- SUPER ART tag f266-299 -->
    <div class="layer" style="z-index:5">
      <div id="mg3-tag">SUPER ART</div>
    </div>
    <!-- HERO NAME f277-349 -->
    <div id="mg3-name-clip" class="layer clip" data-start="{T(277)}" data-duration="{T(F1) - T(277):.4f}" data-track-index="6" style="z-index:6">
      <div id="mg3-name" class="layer">
        <div id="mg3-name-glow" class="layer" style="opacity:0.8"><div class="nm l1">SUKANYA</div><div class="nm l2">DILIP DHARIYA</div></div>
        <div id="mg3-name-main" class="layer"><div class="nm l1">SUKANYA</div><div class="nm l2">DILIP DHARIYA</div></div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      // the two eases of the treatment (section 3): entrance cubic-bezier(0.16,1,0.3,1), exit cubic-bezier(0.7,0,0.84,0)
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
      gsap.set("#mg3-slam", {{ x: 1150 }});
      {js_body}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["mg3_band"] = tl;
    }})();
  </script>
</template>
"""
open(os.path.join(MG, "compositions/mg3_band.html"), "w").write(scene)

GSAP = '<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
index = f"""<!doctype html>
<!-- MG3 band chain, MASTER-TIMED mount: the scene host sits at master f261 = 10.44 s (root = master length to f349). -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=2160, height=3840" />
    {GSAP}
    <style>html, body {{ margin: 0; width: 2160px; height: 3840px; overflow: hidden; background: transparent; }}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{F1 / FPS}" data-fps="{FPS}" data-width="2160" data-height="3840">
      <div id="mg3_band" data-composition-id="mg3_band" data-composition-src="compositions/mg3_band.html"
        data-start="{F0 / FPS}" data-duration="{DUR}" data-track-index="1" data-track-kind="graphics" data-width="2160" data-height="3840"></div>
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
open(os.path.join(MG, "index.html"), "w").write(index)
geo = dict(band_poly=band_pts, echo_up_poly=eu_pts, echo_dn_poly=ed_pts, plate_rot_deg=-12, plate_box=[CX - BW / 2, CY - BH / 2, BW, BH],
           name=dict(font="Barlow Condensed 900 Italic", l1=dict(text="SUKANYA", size_px=S1, cap_px=300, baseline_y=BL1),
                     l2=dict(text="DILIP DHARIYA", size_px=S2, cap_px=220, baseline_y=BL2), centre_x=CX, block_centre_y=CY,
                     tracking_em=0.01, fill=P["ki_white"], glow=f'{P["saffron"]} blur 18px 80%', shadow=f'{P["mulberry"]} 0,+18'),
           slam_x_by_frame={261: 1150, 262: 160, 263: -72, 264: 0})
json.dump(geo, open(os.path.join(MG, "geometry.json"), "w"), indent=1)
print("wrote scene, index, geometry")
