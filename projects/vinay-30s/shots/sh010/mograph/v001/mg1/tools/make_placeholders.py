#!/usr/bin/env python3
"""Placeholder plates for MG1 (until edit/color plates land). Half-res, rough duotone via .cube."""
import json, subprocess, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJ = os.path.abspath(os.path.join(ROOT, '../../../../..'))
cues = json.load(open(os.path.join(PROJ, 'shots/sh010/director/v001/cues.json')))
trailer = os.path.join(PROJ, 'source/trailer.mp4')
out = os.path.join(ROOT, 'placeholder')
INK = (7, 6, 10); WH = (255, 248, 236)
def hx(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def lerp(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def grad(hue, l):
    h = hx(hue); dark = tuple(c * 0.45 for c in h)
    stops = [(0, INK), (0.28, dark), (0.6, h), (0.86, lerp(h, WH, 0.45)), (1, WH)]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if l <= b: return lerp(ca, cb, (l - a) / (b - a))
    return WH
def cube(hue, path, n=17):
    with open(path, 'w') as f:
        f.write(f'LUT_3D_SIZE {n}\n')
        for b in range(n):
            for g in range(n):
                for r in range(n):
                    l = (0.2126 * r + 0.7152 * g + 0.0722 * b) / (n - 1)
                    c = grad(hue, l)
                    f.write('%.5f %.5f %.5f\n' % tuple(x / 255 for x in c))
for s in cues['shots']:
    if s['f_in'] > 357: continue
    w, h = (1080, 452) if s['layer'] == 'roster' else (1080, 604)
    vf = [f"crop={s['crop']}", f"setpts=(PTS-STARTPTS)/{s['speed']}", 'fps=25', f'scale={w}:{h}:flags=lanczos']
    if s['hue']:
        lut = os.path.join(out, f"{s['id']}.cube"); cube(s['hue'], lut)
        vf.append(f'lut3d={lut}')
    dst = os.path.join(out, f"{s['id']}.mp4")
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(s['src_in']), '-i', trailer, '-vf', ','.join(vf),
           '-frames:v', str(s['frames']), '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-g', '1', dst]
    subprocess.run(cmd, check=True); print(s['id'], s['frames'])
