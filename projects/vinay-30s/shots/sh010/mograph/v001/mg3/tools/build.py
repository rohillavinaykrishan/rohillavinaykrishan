#!/usr/bin/env python3
"""MG3 builder: Flurry + Wall + Title (master f387-749), SPECTRUM / sh010.

Generates from cues.json + name_layout.json (MG2) + kit.js + whatever plates exist:
  compositions/mg3.html   THE DELIVERABLE scene: 2160x3840, MASTER time (scene t = f/25), transparent
  index.html              4K root that mounts mg3 at t=0 for 30 s (what the comp lead imports / mirrors)
  proxy/                  540x960 project (scene offset to f387, stage x0.25, Ink bg) -> mg3_proxy_540.mp4
and stages assets/ (symlinked plates, extracted last-frame stills, logo, fonts).

Plate priority: color/v001/plates > edit/v001/plates > ./placeholders (mine, low-res).
Re-run after any upstream hand-off:  python3 tools/build.py
"""
import json, os, subprocess

P = "/home/user/rohillavinaykrishan/projects/vinay-30s"
SH = f"{P}/shots/sh010"
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
cues = json.load(open(f"{SH}/director/v001/cues.json"))
FPS = cues["fps"]
F0, F1 = 387, 749                      # MG3 owns f387..f749 inclusive
END = F1 + 1
pal = cues["palette"]
RAISED, SMOKE = pal["Ink Raised"], pal["Smoke"]
WHITE, BONE, GOLD = pal["White Hot"], pal["Bone"], pal["Champion Gold"]
WHEEL = list(pal["fighters"].values())  # Ryu..Honda, wheel order
L = cues["layout_4k"]
WX, WY, WW, WH = L["act3_window"]
ev = cues["events"]
F_SHOTS = [s for s in cues["shots"] if s["id"].startswith("F")]
TILES = cues["tiles"]
TITLE = ev["TITLE_STINGER"]["f"]       # 686
SPLIT = ev["split_to_wall"]["f"]       # 485
ROLE_IN = ev["role_line_in"]["f"]      # 387
RULE_F = F_SHOTS[1]["f_in"]            # 398 (F2 cut)
log = []

# ---------------------------------------------------------------- inputs
def pick(name):
    for d, tag in ((f"{SH}/color/v001/plates", "color"), (f"{SH}/edit/v001/plates", "edit"),
                   (f"{HERE}/placeholders", "placeholder")):
        if os.path.exists(f"{d}/{name}"):
            return f"{d}/{name}", tag
    return None, None

def stage(src, dst_rel):
    dst = f"{HERE}/{dst_rel}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        os.remove(dst)
    os.symlink(src, dst)

def last_frame(src, dst_rel, n):
    dst = f"{HERE}/{dst_rel}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"select=eq(n\\,{n-1})",
                    "-frames:v", "1", dst], check=True)

for s in F_SHOTS:
    src, tag = pick(f"{s['id']}.mp4")
    stage(src, f"assets/plates/{s['id']}.mp4"); log.append(f"{s['id']}: {tag}")
src9, _ = pick(f"{F_SHOTS[-1]['id']}.mp4")
last_frame(src9, "assets/stills/F9_last.png", F_SHOTS[-1]["f_out"] - F_SHOTS[-1]["f_in"])
for t in TILES:
    for kind in ("duo", "true"):
        src, tag = pick(f"{t['id']}_{kind}.mp4")
        if src is None:                 # an ungraded edit plate stands in for both
            src, tag = pick(f"{t['id']}.mp4"); tag = f"{tag} (ungraded {t['id']}.mp4)"
        stage(src, f"assets/plates/{t['id']}_{kind}.mp4"); log.append(f"{t['id']}_{kind}: {tag}")
        last_frame(src, f"assets/stills/{t['id']}_{kind}_last.png", t["clip_frames"])
stage(f"{P}/assets_prev/sf_logo_alpha.png", "assets/sf_logo_alpha.png")
KIT = open(f"{SH}/mograph/v001/kit/kit.js").read()
log.append("kit: mograph/v001/kit/kit.js (inlined)")
NL = json.load(open(f"{SH}/mograph/v001/name_layout.json"))
log.append(f"name_layout: MG2 {NL.get('version')}")

# ---------------------------------------------------------------- scene writer
def T(f, off):
    return round((f - off) / FPS, 4)

def scene(cid, off, scale):
    els, js = [], []
    z = [10]
    def clip(f_in, f_out, attrs, inner="", tag="div", cls="", style=""):
        z[0] += 1
        close = "" if tag == "img" else f"{inner}</{tag}>"
        return (f'<{tag} {attrs} class="{("clip " + cls).strip()}" data-start="{T(f_in, off)}" '
                f'data-duration="{round((f_out - f_in) / FPS, 4)}" data-track-index="{z[0]}" '
                f'style="{style}z-index:{z[0]}">{close}')
    S = lambda f: max(0.0, T(f - 0.5, off))   # instant 'set' that lands on frame f
    A = lambda f: T(f, off)

    # back canvas: dust (ambient), lowest
    els.append(f'<canvas id="{cid}-bk" data-layout-ignore data-layout-allow-occlusion class="fxc" style="z-index:1"></canvas>')

    # ---- Act-3 window: F1-F9 hard cuts (f387-484); border flashes the next hue for 2 f per cut
    win = [clip(s["f_in"], s["f_out"], f'id="{cid}-{s["id"]}" src="assets/plates/{s["id"]}.mp4" muted playsinline', tag="video")
           for s in F_SHOTS]
    # untimed container (videos are timed); shown f387-484 by opacity
    els.append(f'<div id="{cid}-win" style="z-index:{z[0]}">' + "".join(win) + f'<div id="{cid}-winb" class="winb"></div></div>')
    if off >= F0:   # proxy starts on f387: window visible from its first frame
        js.append(f'gsap.set("#{cid}-win",{{opacity:1}});')
    else:
        js.append(f'tl.set("#{cid}-win",{{opacity:1}},{S(F0)});')
    js.append(f'tl.set("#{cid}-win",{{opacity:0}},{S(SPLIT)});')
    for k, s in enumerate(F_SHOTS):
        js.append(f'tl.set("#{cid}-winb",{{borderColor:"{WHEEL[k % 8]}"}},{S(s["f_in"])});'
                  f'tl.set("#{cid}-winb",{{borderColor:"{SMOKE}"}},{S(s["f_in"] + 2)});')

    # ---- shatter f485: 8 pieces of the frozen F9 frame snap into the tile rects (6 f), become tile backs
    for i, t in enumerate(TILES):
        c, r = i % 4, i // 4
        pw, ph = WW / 4, WH / 2
        px, py = WX + c * pw, WY + r * ph
        tx, ty, tw, th = t["rect_4k"]
        pid = f"{cid}-pc{i+1}"
        els.append(clip(SPLIT, END, f'id="{pid}w" data-layout-allow-overflow',
            f'<div id="{pid}" class="piece" style="left:{px}px;top:{py}px;width:{pw}px;height:{ph}px">'
            f'<img id="{pid}i" src="assets/stills/F9_last.png" style="left:{-c*pw}px;top:{-r*ph}px;width:{WW}px;height:{WH}px"></div>'))
        js.append(f'tl.fromTo("#{pid}",{{x:0,y:0,scaleX:1,scaleY:1}},{{x:{tx-px},y:{ty-py},scaleX:{tw/pw:.4f},scaleY:{th/ph:.4f},'
                  f'duration:{6/FPS},ease:EOUT}},{A(SPLIT)});')
        js.append(f'tl.fromTo("#{pid}i",{{opacity:1}},{{opacity:0,duration:{6/FPS},ease:EIN}},{A(SPLIT + 3)});')

    # ---- tiles T1-T8: kit brush wipe in hue (6 f), 40 f duo clip, duo freeze, true freeze from f686
    for i, t in enumerate(TILES):
        tx, ty, tw, th = t["rect_4k"]
        tid = f"{cid}-t{i+1}"
        a, fr = t["arrive_f"], t["freeze_from_f"]
        inner = (f'<div id="{tid}m" class="tmask">'
                 + clip(a, fr, f'id="{tid}v" src="assets/plates/{t["id"]}_duo.mp4" muted playsinline', tag="video")
                 + clip(fr, END, f'id="{tid}fd" src="assets/stills/{t["id"]}_duo_last.png"', tag="img")
                 + clip(TITLE, END, f'id="{tid}ft" src="assets/stills/{t["id"]}_true_last.png"', tag="img")
                 + f'</div><div id="{tid}b" class="tborder" style="border-color:{t["hue"]}"></div>'
                 f'<div id="{tid}tag" class="ttag" style="color:{t["hue"]}">{t["character"].upper()}</div>')
        z[0] += 1   # untimed container: its media/stills are timed; border + tag fade in on arrival
        els.append(f'<div id="{tid}" class="tile" data-layout-allow-overflow style="left:{tx}px;top:{ty}px;width:{tw}px;height:{th}px;z-index:{z[0]}">{inner}</div>')
        js.append(f'tl.fromTo(["#{tid}b","#{tid}tag"],{{opacity:0}},{{opacity:1,duration:{6/FPS},ease:EOUT}},{A(a + 2)});')
        js.append(f'tl.fromTo("#{tid}b",{{borderColor:"{t["hue"]}"}},{{borderColor:"{GOLD}",duration:{6/FPS},ease:EOUT,immediateRender:false}},{A(TITLE)});')
        js.append(f'tl.fromTo("#{tid}tag",{{color:"{t["hue"]}"}},{{color:"{BONE}",duration:{6/FPS},ease:EOUT,immediateRender:false}},{A(TITLE)});')

    # ---- name canvas (MG2 geometry + MG2's settled look), always on from f387
    els.append(clip(F0, END, f'id="{cid}-namew" data-layout-allow-overflow',
                    f'<canvas id="{cid}-name" data-layout-ignore data-layout-allow-occlusion class="fxc"></canvas>'))

    # ---- role line, rule, STREET FIGHTER · DNEG
    ry, sy2 = L["role_lines_y"]
    els.append(clip(ROLE_IN, END, f'id="{cid}-role"',
        f'<div id="{cid}-rolei" class="role" style="top:{ry - 46}px">SR. MATCHMOVE ARTIST</div>'))
    js.append(f'tl.fromTo("#{cid}-rolei",{{y:24,opacity:0}},{{y:0,opacity:1,duration:{6/FPS},ease:EOUT}},{A(ROLE_IN)});')
    rule_y = round((ry + 46 + sy2 - 32) / 2) - 3
    els.append(clip(RULE_F, END, f'id="{cid}-rule"', f'<div id="{cid}-rulei" class="rule" style="top:{rule_y}px"></div>'))
    js.append(f'tl.fromTo("#{cid}-rulei",{{scaleX:0}},{{scaleX:1,duration:{6/FPS},ease:EOUT}},{A(RULE_F)});')
    els.append(clip(SPLIT, END, f'id="{cid}-sf"',
        f'<div id="{cid}-sfi" class="sfd" style="top:{sy2 - 32}px">STREET FIGHTER&nbsp;&nbsp;·&nbsp;&nbsp;DNEG</div>'))
    js.append(f'tl.fromTo("#{cid}-sfi",{{y:16,opacity:0}},{{y:0,opacity:1,duration:{9/FPS},ease:EOUT}},{A(SPLIT)});')

    # ---- logo slam f686 (1.12 -> 0.97 -> 1.0 in 5 f, 3 % overshoot) + White Hot flash 40 % / 15 %
    lx, ly, lw, lh = L["logo_box"]
    lgw = round(lh * 1618 / 862)
    els.append(clip(TITLE, END, f'id="{cid}-logo"',
        f'<img id="{cid}-logoi" src="assets/sf_logo_alpha.png" style="left:{lx + (lw - lgw) // 2}px;top:{ly}px;width:{lgw}px;height:{lh}px">'))
    js.append(f'tl.fromTo("#{cid}-logoi",{{scale:1.12}},{{scale:0.97,duration:{3/FPS},ease:EOUT}},{A(TITLE)});'
              f'tl.to("#{cid}-logoi",{{scale:1,duration:{2/FPS},ease:EOUT}},{A(TITLE + 3)});')
    els.append(clip(TITLE, TITLE + 2, f'id="{cid}-flash"', f'<div id="{cid}-flashi" class="flash"></div>'))
    js.append(f'tl.set("#{cid}-flashi",{{opacity:0.40}},{A(TITLE)});tl.set("#{cid}-flashi",{{opacity:0.15}},{S(TITLE + 1)});')

    # front canvas: brush fringes
    els.append(f'<canvas id="{cid}-fr" data-layout-ignore data-layout-allow-occlusion class="fxc" style="z-index:900"></canvas>')

    # ---- final hold: 0.5 % ambient push on the whole MG3 stage
    js.append(f'tl.fromTo("#{cid}-push",{{scale:1}},{{scale:1.005,duration:{(END - TITLE - 1)/FPS},ease:"none",immediateRender:false}},{A(TITLE + 1)});')

    dur = round((END - off) / FPS, 4)
    rims = [[s["f_in"], WHEEL[k % 8]] for k, s in enumerate(F_SHOTS)]
    tiles_js = [[t["arrive_f"], t["hue"], t["rect_4k"]] for t in TILES]
    css = f"""
    @font-face {{ font-family:"Unbounded"; font-weight:900; src:url("assets/fonts/Unbounded-900.ttf"); }}
    @font-face {{ font-family:"Unbounded"; font-weight:500; src:url("assets/fonts/Unbounded-500.ttf"); }}
    @font-face {{ font-family:"SpaceMonoHF"; font-weight:700; src:url("assets/fonts/SpaceMono-700.ttf"); }}
    #root {{ position:absolute; inset:0; overflow:hidden; }}
    #{cid}-stage {{ position:absolute; left:0; top:0; width:2160px; height:3840px; transform-origin:0 0; }}
    #{cid}-push {{ position:absolute; left:0; top:0; width:2160px; height:3840px; transform-origin:1080px 2300px; }}
    #{cid}-push > .clip {{ position:absolute; left:0; top:0; width:2160px; height:3840px; }}
    .fxc {{ position:absolute; left:0; top:0; width:2160px; height:3840px; pointer-events:none; }}
    #{cid}-bk, #{cid}-fr {{ mix-blend-mode:screen; }}   /* kit light layers are additive */
    #{cid}-win {{ position:absolute; opacity:0; left:{WX}px; top:{WY}px; width:{WW}px; height:{WH}px; background:{RAISED}; overflow:hidden; }}
    #{cid}-win video {{ position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; }}
    .winb {{ position:absolute; inset:0; border:4px solid {SMOKE}; z-index:99; }}
    .piece {{ position:absolute; overflow:hidden; transform-origin:0 0; background:{RAISED}; outline:2px solid {SMOKE}; outline-offset:-2px; }}
    .piece img {{ position:absolute; max-width:none; }}
    .tile {{ position:absolute; }}
    .tborder, .ttag {{ opacity:0; }}
    .tmask {{ position:absolute; inset:0; overflow:hidden; }}
    .tmask > .clip {{ position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; }}
    .tborder {{ position:absolute; inset:0; border:3px solid; z-index:50; }}
    .ttag {{ position:absolute; left:3px; bottom:3px; z-index:51; font-family:"SpaceMonoHF"; font-weight:700; font-size:28px;
             letter-spacing:0.2em; line-height:1; padding:10px 10px 8px 14px; background:rgba(7,6,10,0.82); white-space:nowrap; }}
    .role {{ position:absolute; left:0; width:2160px; text-align:center; font-family:"Unbounded"; font-weight:500; font-size:92px;
             line-height:1; letter-spacing:0.18em; padding-left:0.18em; color:{WHITE}; white-space:nowrap; }}
    .rule {{ position:absolute; left:{1080 - 260}px; width:520px; height:6px; background:{GOLD}; transform-origin:50% 50%; }}
    .sfd {{ position:absolute; left:0; width:2160px; text-align:center; font-family:"Unbounded"; font-weight:500; font-size:64px;
            line-height:1; letter-spacing:0.30em; padding-left:0.30em; color:{BONE}; white-space:nowrap; }}
    #{cid}-logoi {{ position:absolute; transform-origin:50% 50%; }}
    .flash {{ position:absolute; inset:0; background:{WHITE}; opacity:0; }}
    """
    nl_min = {"font": NL["font"], "lines": [{"baseline_y": l["baseline_y"],
              "glyphs": [{"ch": g["ch"], "pen_x": g["pen_x"]} for g in l["glyphs"]]} for l in NL["lines"]]}
    draw_js = f"""
    const OFF = {off}, PX = {scale};            // canvas backing px per 4K px
    const NL = {json.dumps(nl_min)};
    const RIMS = {json.dumps(rims)}, TILES = {json.dumps(tiles_js)};
    const PAL = FX.palette, WHITE = PAL.whiteHot, GOLD = PAL.gold, GOLDD = PAL.goldDeep;
    const W4 = 2160, H4 = 3840;
    function mk(el) {{ const c = el || document.createElement("canvas"); c.width = Math.round(W4 * PX); c.height = Math.round(H4 * PX); return c; }}
    const nmC = mk(document.getElementById("{cid}-name")), bkC = mk(document.getElementById("{cid}-bk")), frC = mk(document.getElementById("{cid}-fr"));
    const nm = nmC.getContext("2d"), bk = bkC.getContext("2d"), fr = frC.getContext("2d");
    const tmpC = mk(), tmp = tmpC.getContext("2d");
    const reset = (c) => {{ c.setTransform(PX, 0, 0, PX, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = "source-over"; c.filter = "none"; }};
    const FONT = "900 " + NL.font.size_px + "px Unbounded";
    // same glyph placement as MG2 (each glyph at pen_x on its baseline)
    function nameAt(c, ox, oy, mode) {{
      c.save(); c.translate(ox, oy); c.font = FONT; c.textBaseline = "alphabetic"; c.textAlign = "left";
      for (const ln of NL.lines) for (const g of ln.glyphs) {{
        if (mode !== "fill") c.strokeText(g.ch, g.pen_x, ln.baseline_y);
        if (mode !== "stroke") c.fillText(g.ch, g.pen_x, ln.baseline_y);
      }}
      c.restore();
    }}
    const cache = new Map();
    function glowName(colour, blur, stroke) {{   // blurred copy of the name, cached
      const key = colour + "|" + blur + "|" + stroke;
      if (cache.has(key)) return cache.get(key);
      reset(tmp); tmp.clearRect(0, 0, W4, H4);
      tmp.fillStyle = colour; tmp.strokeStyle = colour; tmp.lineWidth = stroke; tmp.lineJoin = "round";
      nameAt(tmp, 0, 0, stroke > 0 ? "both" : "fill");
      const out = mk(), o = out.getContext("2d");
      o.filter = "blur(" + (blur * PX) + "px)"; o.drawImage(tmpC, 0, 0);
      cache.set(key, out); return out;
    }}
    const pr = FX.prog, EO = FX.ease.out, EI = FX.ease.in;
    function drawName(f) {{
      reset(nm); nm.clearRect(0, 0, W4, H4);
      if (f < {F0} - 0.01) return;
      // breath f634-669: the gold glow swells once
      const br = f >= 634 && f <= 669 ? Math.sin(Math.PI * (f - 634) / 35) : 0;
      // MG2's settled look: gold glow 45 % (18 px) + 30 % (36 px), Gold Deep keyline (0,+6), White Hot fill
      nm.save(); nm.setTransform(1, 0, 0, 1, 0, 0);
      nm.globalAlpha = Math.min(1, 0.45 * (1 + 0.6 * br)); nm.drawImage(glowName(GOLD, 18, 10), 0, 0);
      nm.globalAlpha = Math.min(1, 0.30 * (1 + 1.2 * br)); nm.drawImage(glowName(GOLD, 36, 10), 0, 0);
      nm.restore();
      // rim pulse: on every flurry cut the rim takes that cut's hue at 30 %, decaying over 4 f
      for (const [rf, hex] of RIMS) {{
        if (f >= rf - 0.01 && f < rf + 4) {{
          const a = 0.30 * (1 - EI(pr(f, rf, rf + 4)));
          nm.save(); nm.setTransform(1, 0, 0, 1, 0, 0); nm.globalCompositeOperation = "lighter";
          nm.globalAlpha = a; nm.drawImage(glowName(hex, 14, 16), 0, 0); nm.restore();
          nm.save(); nm.globalAlpha = Math.min(1, a * 2); nm.strokeStyle = hex; nm.lineWidth = 10; nm.lineJoin = "round"; nameAt(nm, 0, 0, "stroke"); nm.restore();
        }}
      }}
      nm.save(); nm.fillStyle = GOLDD; nm.strokeStyle = GOLDD; nm.lineWidth = 4; nm.lineJoin = "round"; nameAt(nm, 0, 6, "both"); nm.restore();
      nm.save(); nm.fillStyle = WHITE; nameAt(nm, 0, 0, "fill"); nm.restore();
      // light sweep f651-669: a White Hot glow band crosses the name L->R (linear)
      if (f >= 651 && f < 670) {{
        const x = -300 + pr(f, 651, 669) * (W4 + 600);
        reset(tmp); tmp.clearRect(0, 0, W4, H4);
        tmp.setTransform(1, 0, 0, 1, 0, 0); tmp.drawImage(glowName(WHITE, 22, 6), 0, 0);
        tmp.setTransform(PX, 0, 0, PX, 0, 0); tmp.globalCompositeOperation = "destination-in";
        const g = tmp.createLinearGradient(x - 260, 0, x + 260, 0);
        g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(0.5, "rgba(0,0,0,1)"); g.addColorStop(1, "rgba(0,0,0,0)");
        tmp.fillStyle = g; tmp.fillRect(0, 0, W4, H4);
        nm.save(); nm.setTransform(1, 0, 0, 1, 0, 0); nm.globalCompositeOperation = "lighter"; nm.globalAlpha = 0.9;
        nm.drawImage(tmpC, 0, 0); nm.drawImage(tmpC, 0, 0); nm.restore();
      }}
    }}
    const maskC = [], maskEl = [];
    TILES.forEach((t, i) => {{
      const c = document.createElement("canvas"); c.width = Math.max(1, Math.round(t[2][2] * PX)); c.height = Math.max(1, Math.round(t[2][3] * PX));
      maskC.push(c); maskEl.push(document.getElementById("{cid}-t" + (i + 1) + "m"));
    }});
    function setMask(el, v) {{ el.style.webkitMaskImage = v; el.style.maskImage = v; el.style.webkitMaskSize = "100% 100%"; el.style.maskSize = "100% 100%"; }}
    function drawTiles(f) {{
      reset(fr); fr.clearRect(0, 0, W4, H4);
      TILES.forEach(([a, hex, r], i) => {{
        const p = FX.wipeProgress(f, a, 6), opt = {{ variant: i % 3, seed: i + 1, s: 1 }};
        const el = maskEl[i];
        if (p >= 1) {{ setMask(el, "none"); return; }}
        if (p <= 0) {{ setMask(el, "linear-gradient(transparent, transparent)"); return; }}
        const c = maskC[i], m = c.getContext("2d");
        m.setTransform(PX, 0, 0, PX, 0, 0); m.clearRect(0, 0, r[2], r[3]);
        FX.brushMatte(m, [0, 0, r[2], r[3]], p, opt);
        setMask(el, "url(" + c.toDataURL() + ")");
        FX.brushFringe(fr, r, p, hex, opt);
      }});
    }}
    function drawBack(f) {{
      reset(bk); bk.clearRect(0, 0, W4, H4);
      if (f >= 634) {{ bk.save(); bk.globalAlpha = EO(pr(f, 634, 660)); FX.dust(bk, f, {{ count: 90, s: 1, opacity: 0.5 }}); bk.restore(); }}
    }}
    function draw(f) {{ f = Math.round(f * 1000) / 1000; drawBack(f); drawName(f); drawTiles(f); }}
    """
    return f"""<template>
  <style>{css}</style>
  <div id="root" data-composition-id="{cid}" data-width="2160" data-height="3840" data-start="0" data-duration="{dur}">
    <div id="{cid}-stage" data-layout-allow-overflow><div id="{cid}-push" data-layout-allow-overflow data-layout-allow-overlap>
    {chr(10).join(els)}
    </div></div>
  </div>
  <script>
    /* ===== kit.js (mograph/v001/kit, inlined at build time) ===== */
    {KIT}
  </script>
  <script>
    // MG3 'SPECTRUM' flurry + wall + title. GENERATED by tools/build.py; scene time {'= master frame / 25' if off == 0 else f'= (master frame - {off}) / 25'}.
    const EOUT = (p) => FX.ease.out(p);   // entrances cubic-bezier(0.16,1,0.3,1)
    const EIN  = (p) => FX.ease.in(p);    // exits     cubic-bezier(0.7,0,0.84,0)
    const tl = gsap.timeline({{ paused: true }});
    gsap.set("#{cid}-stage", {{ scale: {scale} }});
    {draw_js}
{chr(10).join('    ' + j for j in js)}
    const drv = {{ t: 0 }};
    tl.fromTo(drv, {{ t: 0 }}, {{ t: {dur}, duration: {dur}, ease: "none", onUpdate: () => draw(OFF + drv.t * {FPS}) }}, 0);
    // canvas text needs Unbounded loaded first: register the timeline only after the fonts resolve
    Promise.all([document.fonts.load(FONT), document.fonts.load("500 92px Unbounded"), document.fonts.load("700 28px SpaceMonoHF")])
      .then(() => {{ cache.clear(); draw(OFF); window.__timelines["{cid}"] = tl; }});
  </script>
</template>
"""

def root(cid_root, scene_id, src, w, h, dur, bg):
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ width:{w}px; height:{h}px; overflow:hidden; background:{bg}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="{cid_root}" data-start="0" data-duration="{dur}" data-fps="25" data-width="{w}" data-height="{h}">
      <div id="{scene_id}" data-composition-id="{scene_id}" data-composition-src="{src}" data-start="0" data-duration="{dur}"
           data-track-index="1" data-track-kind="graphics" data-width="{w}" data-height="{h}"></div>
    </div>
    <script>
      window.__timelines["{cid_root}"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""

os.makedirs(f"{HERE}/compositions", exist_ok=True)
open(f"{HERE}/compositions/mg3.html", "w").write(scene("mg3", 0, 1))
open(f"{HERE}/index.html", "w").write(root("main", "mg3", "compositions/mg3.html", 2160, 3840, END / FPS, "transparent"))
# proxy = its own tiny HyperFrames project (one root per project), sharing ../assets
PX_DIR = f"{HERE}/proxy"
os.makedirs(f"{PX_DIR}/compositions", exist_ok=True)
if not os.path.lexists(f"{PX_DIR}/assets"):
    os.symlink("../assets", f"{PX_DIR}/assets")
for fn in ("hyperframes.json", "package.json"):
    open(f"{PX_DIR}/{fn}", "w").write(open(f"{HERE}/{fn}").read())
open(f"{PX_DIR}/compositions/mg3p.html", "w").write(scene("mg3p", F0, 0.25))
open(f"{PX_DIR}/index.html", "w").write(root("proxy", "mg3p", "compositions/mg3p.html", 540, 960, round((END - F0) / FPS, 4), pal["Ink"]))
for old in (f"{HERE}/proxy.html", f"{HERE}/compositions/mg3p.html"):
    if os.path.exists(old): os.remove(old)
json.dump({"inputs": log}, open(f"{HERE}/build_inputs.json", "w"), indent=1)
print("\n".join(log))
