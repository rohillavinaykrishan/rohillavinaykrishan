#!/usr/bin/env python3
"""sh010 comp v001: assemble the master HyperFrames composition from the upstream sub-comps.

Re-run any time an upstream part changes. It:
  * copies each sub-comp scene file into master/compositions/ with its asset paths namespaced
    (assets/x -> assets/<ns>/x) and symlinks master/assets/<ns> -> the upstream assets dir;
  * points MG1's nested roll host at the FINAL roll (roll/v001/roll.html);
  * writes a labelled placeholder scene for any part that has not landed yet;
  * applies the comp-lead ownership overrides (OVERRIDES below);
  * writes master/index.html (2160x3840, 25 fps, 18.0 s) and status.json.
"""
import json, os, re, sys, shutil

SH = "/home/user/rohillavinaykrishan/projects/sukanya-v2/shots/sh010"
M = f"{SH}/comp/v001/master"
FPS = 25

# id, upstream scene file, upstream assets dir, master frame in, frame out (exclusive), z-index
PARTS = [
    ("mg1", f"{SH}/mograph/v001/mg1_roster/compositions/mg1.html", f"{SH}/mograph/v001/mg1_roster/assets", 0, 261, 2),
    ("mg3_band", f"{SH}/mograph/v001/mg3_band/compositions/mg3_band.html", f"{SH}/mograph/v001/mg3_band/assets", 261, 350, 3),
    ("mg2", f"{SH}/mograph/v001/mg2_superart/compositions/mg2.html", f"{SH}/mograph/v001/mg2_superart/assets", 243, 277, 4),
    ("mg4_title", None, f"{SH}/mograph/v001/mg4_title/assets", 350, 450, 5),
]
ROLL = (f"{SH}/roll/v001/roll.html", f"{SH}/roll/v001/preview/assets")
AUDIO = f"{SH}/sound/v001/master.wav"

# comp-lead overrides: extra CSS appended inside a part's <template><style> (ownership decisions)
OVERRIDES = {}
ovr_file = f"{SH}/comp/v001/tools/overrides.json"
if os.path.exists(ovr_file):
    OVERRIDES = json.load(open(ovr_file))


def find_mg4():
    d = f"{SH}/mograph/v001/mg4_title/compositions"
    if os.path.isdir(d):
        c = sorted(f for f in os.listdir(d) if f.endswith(".html"))
        if c:
            return f"{d}/{c[0]}"
    return None


def link(ns, src):
    dst = f"{M}/assets/{ns}"
    if os.path.islink(dst) or os.path.exists(dst):
        if os.path.islink(dst):
            os.unlink(dst)
        else:
            shutil.rmtree(dst)
    os.symlink(src, dst)


def namespace(html, ns):
    return re.sub(r'(["\'(])assets/', r"\1assets/%s/" % ns, html)


def comp_id(html):
    m = re.search(r'data-composition-id="([^"]+)"', html)
    return m.group(1) if m else None


def placeholder(cid, f0, f1, label):
    dur = (f1 - f0) / FPS
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    #{cid}-ph {{ position: absolute; left: 160px; top: 1500px; width: 1840px; height: 840px; border: 6px dashed #FFB12A;
      color: #FFF3DC; font: 600 96px/1.3 Montserrat, sans-serif; text-align: center; padding-top: 220px; box-sizing: border-box; }}
    #{cid}-phf {{ position: absolute; left: 0; top: 2500px; width: 2160px; text-align: center; color: #D9CFC3; font: 500 64px Montserrat; }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="2160" data-height="3840">
    <div id="{cid}-ph">PLACEHOLDER<br>{label}<br>f{f0}-f{f1 - 1}</div>
    <div id="{cid}-phf">0</div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const o = {{ f: 0 }}, el = document.getElementById("{cid}-phf");
      tl.to(o, {{ f: {f1 - f0 - 1}, duration: {dur - 1 / FPS:.4f}, ease: "none",
        onUpdate: () => {{ el.textContent = "master f" + Math.round({f0} + o.f); }} }}, 0);
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""


def inject_css(html, css):
    return html.replace("</style>", css + "\n  </style>", 1) if css else html


def main():
    os.makedirs(f"{M}/compositions", exist_ok=True)
    os.makedirs(f"{M}/assets", exist_ok=True)
    status = {}

    # final roll (MG1 nests it as compositions/roll.html)
    roll = namespace(open(ROLL[0]).read(), "roll")
    open(f"{M}/compositions/roll.html", "w").write(roll)
    link("roll", ROLL[1])
    status["roll"] = {"src": ROLL[0], "real": True, "rows": roll.count('class="rr"')}

    hosts = []
    roll_nested = False
    for cid, src, adir, f0, f1, z in PARTS:
        if cid == "mg4_title":
            src = find_mg4()
        real = bool(src and os.path.exists(src))
        if real:
            html = open(src).read()
            ucid = comp_id(html)
            if ucid and ucid != cid:
                cid = ucid
            html = namespace(html, cid)
            # nested roll host keeps pointing at master compositions/roll.html (the final roll)
            if 'data-composition-src="compositions/roll.html"' in html:
                roll_nested = True
            html = inject_css(html, OVERRIDES.get(cid, ""))
            link(cid, adir)
        else:
            html = placeholder(cid, f0, f1, cid.upper())
        open(f"{M}/compositions/{cid}.html", "w").write(html)
        status[cid] = {"src": src, "real": real, "f_in": f0, "f_out": f1, "mtime": os.path.getmtime(src) if real else None}
        hosts.append((cid, f0, f1, z))

    # audio
    os.makedirs(f"{M}/assets/audio", exist_ok=True)
    a = f"{M}/assets/audio/master.wav"
    if os.path.islink(a):
        os.unlink(a)
    os.symlink(AUDIO, a)

    lines = []
    for cid, f0, f1, z in hosts:
        lines.append(
            f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
            f'data-start="{f0 / FPS:.2f}" data-duration="{(f1 - f0) / FPS:.2f}" data-track-index="{z}" '
            f'data-track-kind="graphics" data-width="2160" data-height="3840" style="z-index:{z}"></div>'
            f"  <!-- master f{f0}-f{f1 - 1} -->")
    if not roll_nested:
        lines.insert(0,
            '      <div id="roll" data-composition-id="roll" data-composition-src="compositions/roll.html" data-start="0" '
            'data-duration="10.44" data-track-index="1" data-track-kind="graphics" data-width="2160" data-height="3840" '
            'style="z-index:1"></div>  <!-- master f0-f260 (direct: MG1 does not nest it) -->')
    status["roll"]["mounted"] = "nested in mg1" if roll_nested else "direct"

    index = f"""<!doctype html>
<!-- sh010 MASTER (comp lead). GENERATED by ../tools/build_master.py: edit the builder, then rebuild.
     2160x3840, 25 fps, 450 frames (18.00 s). Sub-comps mounted by master frame range (cues.json). -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=2160, height=3840" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>html, body {{ margin: 0; width: 2160px; height: 3840px; overflow: hidden; background: #14080F; }}</style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="18.00" data-fps="25" data-width="2160" data-height="3840">
      <div id="master-bg" style="position:absolute;inset:0;background:#14080F;z-index:0"></div>
{chr(10).join(lines)}
      <audio id="master-audio" class="clip" src="assets/audio/master.wav" data-start="0" data-duration="18.00" data-track-index="9" data-volume="1"></audio>
    </div>
    <script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
    open(f"{M}/index.html", "w").write(index)

    # 540x960 review proxy: same hosts at 2160x3840 inside a 0.25 scale wrapper; assets/compositions symlinked
    P = f"{SH}/comp/v001/proxy540"
    os.makedirs(P, exist_ok=True)
    for n in ("assets", "compositions"):
        if not os.path.islink(f"{P}/{n}"):
            os.symlink(f"../master/{n}", f"{P}/{n}")
    proxy = index.replace('width=2160, height=3840', 'width=540, height=960') \
        .replace('html, body { margin: 0; width: 2160px; height: 3840px;',
                 '#proxy-scale { position: absolute; left: 0; top: 0; width: 2160px; height: 3840px; transform: scale(0.25); transform-origin: 0 0; }\n    html, body { margin: 0; width: 540px; height: 960px;') \
        .replace('data-fps="25" data-width="2160" data-height="3840">', 'data-fps="25" data-width="540" data-height="960">\n     <div id="proxy-scale">', 1) \
        .replace('      <audio id="master-audio"', '     </div>\n      <audio id="master-audio"')
    open(f"{P}/index.html", "w").write(proxy)
    json.dump(status, open(f"{SH}/comp/v001/status.json", "w"), indent=1)
    for k, v in status.items():
        print(f"{k:10s} {'REAL' if v['real'] else 'placeholder'}  {v.get('src')}")


if __name__ == "__main__":
    main()
