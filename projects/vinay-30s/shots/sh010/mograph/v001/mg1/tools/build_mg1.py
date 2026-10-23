#!/usr/bin/env python3
"""Build MG1 (Roster + Clash, master f0-356) from cues.json.
Writes: compositions/mg1.html (the 2160x3840 sub-comp), index.html (4K root, for the comp lead),
        proxy.html (540x960 root that mounts the same scene at 0.25), mg1_data.json (what was baked in).
Run tools/sync_inputs.py first (plates/kit -> assets/mg1/)."""
import json, os, html
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SH = os.path.abspath(os.path.join(ROOT, '../../..'))
cues = json.load(open(os.path.join(SH, 'director/v001/cues.json')))
FPS = cues['fps']; W, H = map(int, cues['size'].split('x'))
L = cues['layout_4k']; pal = cues['palette']
LAST = cues['events']['SILENCE']['f'][0] - 1          # 356: MG1 owns f0-356
NF = LAST + 1
roster = [s for s in cues['shots'] if s['layer'] == 'roster']
clash = [s for s in cues['shots'] if s['layer'] == 'clash']
huename = {t['character']: t['hue_name'] for t in cues['tiles']}
beats1 = cues['beats_f']['S1_117.5bpm_12.77f']

# Act-1 outline names: Unbounded 900, cap <= 420 px (font-size 560), +0.04em, fitted to <= NAME_MAXW
CAP_RATIO = 0.75; NAME_MAXW = 1960; NAME_BASE = L['act1_window'][1] - 58
font900 = os.path.join(ROOT, 'assets/mg1/fonts/Unbounded-900.ttf')
def name_size(txt):
    fnt = ImageFont.truetype(font900, 1000)
    w1 = fnt.getlength(txt) / 1000 + 0.04 * (len(txt) - 1)  # width per px of font-size
    return min(420 / CAP_RATIO, NAME_MAXW / w1), w1

data = {
    'W': W, 'H': H, 'fps': FPS, 'lastFrame': LAST, 'duration': NF / FPS,
    'defaults': {'fxScale': 1, 'spirals': True, 'push': True},
    'cardRect': [0, 500, W, 1600], 'win1': L['act1_window'], 'win2': L['act2_window'],
    'wipeDur': 6,
    'coldOpen': {'end': cues['events']['cold_open']['f'][1], 'hairDur': 12, 'labelF': beats1[0]},
    'name': {'x0': 40, 'slide': 80},
    'shutter': {'f0': roster[-1]['f_out'], 'f1': beats1[-1], 'tighten': roster[-1]['f_out'] + 6, 'lineH': 6, 'stagger': 1},
    'clash': {'f0': clash[0]['f_in'], 'slam': 3},
    'charge': {'f0': clash[-1]['f_in'], 'push': 0.04},
    'plume': {'opacity': 0.25}, 'dust': {'count': 90, 'opacity': 0.5},
    'streakTrail': 10,
    'roster': [], 'clashShots': [],
}
for i, s in enumerate(roster):
    ch = s['characters'][0]; txt = ch.upper()
    fs, w1 = name_size(txt)
    data['roster'].append({'id': s['id'], 'f_in': s['f_in'], 'f_out': s['f_out'], 'hue': s['hue'], 'char': ch,
                           'name': txt, 'nameSize': round(fs, 2), 'nameW': round(fs * w1, 1),
                           'tag': f'{i + 1:02d} / {len(roster):02d}', 'hueName': huename.get(ch, '')})
data['clashShots'] = [{'id': s['id'], 'f_in': s['f_in'], 'f_out': s['f_out']} for s in clash]
data['streaks'] = {'win2': L['act2_window'], 'clashCuts': [s['f_in'] for s in clash[:-1]],
                   'speeds': [40, 55, 72, 92, 115], 'burstF': clash[0]['f_in'],
                   'spiralF0': clash[-1]['f_in'], 'spiralF1': LAST, 'centre': [1080, 1550], 'rEnd': 40, 'turns': 2, 'n': 8}
json.dump(data, open(os.path.join(ROOT, 'mg1_data.json'), 'w'), indent=1)

def t(f): return f'{f / FPS:.2f}'
def rgba(hx, a):
    return f'rgba({int(hx[1:3], 16)},{int(hx[3:5], 16)},{int(hx[5:7], 16)},{a})'
e = html.escape
INK, INKR, WH, BONE = pal['Ink'], pal['Ink Raised'], pal['White Hot'], pal['Bone']
w1x, w1y, w1w, w1h = L['act1_window']; w2x, w2y, w2w, w2h = L['act2_window']

cards = []
for i, r in enumerate(data['roster']):
    fs = r['nameSize']; top = NAME_BASE - 0.875 * fs
    cards.append(f'''
    <div class="mg1-card" id="mg1-card-{r['id']}" style="z-index:{10 + i}">
      <div class="mg1-win1">
        <video id="mg1-v-{r['id']}" class="clip" data-start="{t(r['f_in'])}" data-duration="{t(r['f_out'] - r['f_in'])}" data-track-index="{2 + i % 2}" muted playsinline src="assets/mg1/plates/{r['id']}.mp4"></video>
        <img class="mg1-hold" id="mg1-h-{r['id']}" src="assets/mg1/stills/{r['id']}_last.jpg" alt="" />
      </div>
      <div class="mg1-name" id="mg1-n-{r['id']}" style="top:{top:.1f}px;font-size:{fs:.2f}px;height:{fs:.2f}px;line-height:{fs:.2f}px;color:{rgba(r['hue'], 0.12)};-webkit-text-stroke:6px {r['hue']}">{e(r['name'])}</div>
      <div class="mg1-tags" id="mg1-t-{r['id']}"><span class="mg1-tag">{e(r['tag'])}</span><span class="mg1-huename" style="color:{r['hue']}">{e(r['hueName'])}</span></div>
    </div>''')

slivers = []
sh = w1h / len(roster)
for j, r in enumerate(data['roster']):
    slivers.append(f'''
      <div class="mg1-sliver" id="mg1-sl-{j}"><img id="mg1-sli-{j}" src="assets/mg1/stills/{r['id']}_last.jpg" alt="" /><div class="mg1-sltint" id="mg1-slt-{j}" style="background:{r['hue']}"></div></div>''')

clips2 = []
for i, s in enumerate(data['clashShots']):
    clips2.append(f'''
      <video id="mg1-v-{s['id']}" class="clip" data-start="{t(s['f_in'])}" data-duration="{t(s['f_out'] - s['f_in'])}" data-track-index="{4 + i % 2}" muted playsinline src="assets/mg1/plates/{s['id']}.mp4"></video>''')

scene_js = open(os.path.join(HERE, 'mg1_scene.js')).read()
variables = json.dumps([
    {"id": "fxScale", "type": "number", "label": "FX canvas scale (1 = 4K, 0.25 = proxy)", "default": 1, "min": 0.25, "max": 1, "step": 0.25},
    {"id": "spirals", "type": "boolean", "label": "Draw the f336-356 charge spirals (off if MG2 draws them)", "default": True},
    {"id": "push", "type": "boolean", "label": "Whole-frame push 1.00-1.04 f336-356", "default": True}])

scene = f'''<template>
  <style>
    @font-face {{ font-family: "Unbounded"; font-weight: 900; src: url("assets/mg1/fonts/Unbounded-900.ttf") format("truetype"); }}
    @font-face {{ font-family: "Unbounded"; font-weight: 500; src: url("assets/mg1/fonts/Unbounded-500.ttf") format("truetype"); }}
    @font-face {{ font-family: "MG1 Unbounded Outline"; font-weight: 900; src: url("assets/mg1/fonts/Unbounded-900-merged.ttf") format("truetype"); }}
    @font-face {{ font-family: "MG1 Space Mono"; font-weight: 700; src: url("assets/mg1/fonts/SpaceMono-700.ttf") format("truetype"); }}
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    #mg1-ink {{ position: absolute; inset: 0; background: {INK}; }}
    #mg1-stage {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; transform-origin: 1080px 1550px; }}
    #mg1-stage canvas {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; }}
    .mg1-card {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; visibility: hidden; }}
    .mg1-win1 {{ position: absolute; left: {w1x}px; top: {w1y}px; width: {w1w}px; height: {w1h}px; background: {INKR}; overflow: hidden; }}
    .mg1-win1 video, .mg1-win1 img {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
    .mg1-hold {{ opacity: 0; }}
    .mg1-name {{ position: absolute; left: 0; white-space: nowrap; font-family: "MG1 Unbounded Outline"; font-weight: 900; letter-spacing: 0.04em; will-change: transform; }}
    .mg1-tags {{ position: absolute; left: 120px; right: 120px; top: {w1y + w1h + 46}px; display: flex; justify-content: space-between;
                 font-family: "MG1 Space Mono"; font-weight: 700; font-size: 34px; letter-spacing: 0.2em; line-height: 1; }}
    .mg1-tag {{ color: {BONE}; }}
    #mg1-card-C0 {{ z-index: 9; }}
    #mg1-label {{ position: absolute; left: 120px; top: {w1y - 92}px; font-family: "MG1 Space Mono"; font-weight: 700; font-size: 34px;
                  letter-spacing: 0.25em; color: {BONE}; white-space: pre; line-height: 1; opacity: 0; }}
    #mg1-hair {{ position: absolute; left: 0; top: {w1y - 1}px; width: {W}px; height: 2px; background: {WH}; transform-origin: 0 50%; z-index: 30; }}
    #mg1-shutter {{ position: absolute; inset: 0; visibility: hidden; z-index: 25; }}
    .mg1-sliver {{ position: absolute; left: 0; top: 0; width: {W}px; overflow: hidden; }}
    .mg1-sliver img {{ position: absolute; left: 0; top: 0; width: {w1w}px; height: {w1h}px; object-fit: cover; }}
    .mg1-sltint {{ position: absolute; inset: 0; opacity: 0; }}
    #mg1-win2 {{ position: absolute; left: {w2x}px; top: {w2y}px; width: {w2w}px; height: {w2h}px; background: {INKR}; overflow: hidden; visibility: hidden; z-index: 26; }}
    #mg1-win2 video {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
    #mg1-bgfx {{ z-index: 1; }}
    #mg1-fgfx {{ z-index: 40; mix-blend-mode: screen; }}
  </style>
  <div id="root" data-composition-id="mg1" data-width="{W}" data-height="{H}" data-duration="{NF / FPS:.2f}"
       data-composition-variables='{variables}' data-layout-allow-overflow data-layout-allow-overlap>
    <div id="mg1-ink"></div>
    <div id="mg1-stage" data-layout-allow-overflow data-layout-allow-overlap>
      <canvas id="mg1-bgfx"></canvas>
      <div class="mg1-card" id="mg1-card-C0"><div id="mg1-label">STREET FIGHTER  ·  DNEG</div></div>
      {''.join(cards)}
      <div id="mg1-hair"></div>
      <div id="mg1-shutter">{''.join(slivers)}
      </div>
      <div id="mg1-win2">{''.join(clips2)}
      </div>
      <canvas id="mg1-fgfx"></canvas>
    </div>
  </div>
  <script src="assets/mg1/vendor/gsap.min.js"></script>
  <script src="assets/mg1/kit/kit.js"></script>
  <script src="assets/mg1/js/mg1_streaks.js"></script>
  <script>
    window.MG1_DATA = {json.dumps(data, separators=(',', ':'))};
  </script>
  <script>
{scene_js}
  </script>
</template>
'''
open(os.path.join(ROOT, 'compositions/mg1.html'), 'w').write(scene)

def root_doc(w, h, inner, title):
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <title>{title}</title>
    <script src="assets/mg1/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {w}px; height: {h}px; overflow: hidden; background: {INK}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{NF / FPS:.2f}" data-width="{w}" data-height="{h}" data-fps="{FPS}">
{inner}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
host = lambda vals: f'''<div id="mg1" data-composition-id="mg1" data-composition-src="compositions/mg1.html" data-start="0" data-duration="{NF / FPS:.2f}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" data-variable-values='{json.dumps(vals)}'></div>'''
open(os.path.join(ROOT, 'index.html'), 'w').write(root_doc(W, H, '      ' + host({"fxScale": 1}), 'MG1 Roster + Clash (4K, master f0-356)'))
proxy_inner = f'''      <div id="mg1-proxy-wrap" style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;transform:scale(0.25);transform-origin:0 0">
        {host({"fxScale": 0.25})}
      </div>'''
os.makedirs(os.path.join(ROOT, 'proxy'), exist_ok=True)
for d in ('assets', 'compositions'):
    lk = os.path.join(ROOT, 'proxy', d)
    if not os.path.islink(lk): os.symlink('../' + d, lk)
if os.path.exists(os.path.join(ROOT, 'proxy.html')): os.remove(os.path.join(ROOT, 'proxy.html'))
open(os.path.join(ROOT, 'proxy/index.html'), 'w').write(root_doc(W // 4, H // 4, proxy_inner, 'MG1 proxy 540x960'))
print('built mg1:', NF, 'frames;', [(r['id'], r['name'], r['nameSize']) for r in data['roster']])
