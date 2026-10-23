#!/usr/bin/env python3
"""Editor A: build roster plates A01-A13 from cues.json (the only timing source).
Usage: python3 build_plates_A.py [ID ...]   (run from anywhere)
Per shot: trailer frames (inside ONE librarian shot) -> active crop 1280x536 ->
pad 4 rows on TOP (realigns the 8px block grid: active y=92 = 4 mod 8) -> deblock strong/8 ->
crop back -> shot crop -> [minterpolate 75 fps if nearest-frame picking would duplicate] ->
frame-map conform src_t = src_in + (f-f_in)/25*speed -> lanczos cover-scale to 2160x1180 ->
unsharp 5:5:0.4 -> H.264 crf 10 yuv444p 25 fps, exactly f_out-f_in frames."""
import json, math, subprocess, sys, os
ROOT = '/home/user/rohillavinaykrishan'
PRJ = f'{ROOT}/projects/sukanya-v2'
OUT = f'{PRJ}/shots/sh010/edit/v001'
FPS = 24000/1001
W, H = 2160, 1180
cues = json.load(open(f'{PRJ}/shots/sh010/director/v001/cues.json'))
lib = json.load(open(f'{ROOT}/library/streetfighter-trailer/shots.json'))['shots']
# vertical framing for the cover crop: fraction of the spare rows taken from the top (0.5 = centre)
VBIAS = {'A03': 0.25, 'A12': 0.25}

def plan(s):
    n = s['f_out'] - s['f_in']
    speed = (s['src_out'] - s['src_in']) / (n / 25)
    p0 = s['src_in'] * FPS
    step = speed * FPS / 25                     # source frames per master frame
    L = [x for x in lib if x['in_frame'] <= math.floor(p0 + 1e-6) <= x['out_frame']][0]
    clamped = False
    if p0 + (n - 1) * step > L['out_frame']:    # never interpolate past the trailer cut
        step = (L['out_frame'] - p0) / (n - 1); clamped = True
    pos = [p0 + k * step for k in range(n)]
    near = [math.floor(p + 1e-6) for p in pos]
    use_mi = len(set(near)) < n
    a = math.floor(pos[0] + 1e-6)
    b = min(math.ceil(pos[-1] - 1e-6), L['out_frame']) if use_mi else near[-1]
    if use_mi:
        kmax = math.floor((b - a) / FPS * 75 + 1e-6)   # last 75fps frame at/before the last real input frame
        picks = [min(round((p - a) / FPS * 75), kmax) for p in pos]
        assert len(set(picks)) == n
    else:
        picks = [x - a for x in near]
    assert L['in_frame'] <= a and b <= L['out_frame'], 'crosses a trailer cut'
    return dict(n=n, speed=speed, eff_speed=step * 25 / FPS, a=a, b=b, lib=L, mi=use_mi,
                picks=picks, clamped=clamped, src_frames=near)

def build(s):
    p = plan(s)
    cw, ch, cx, cy = [int(v) for v in s['crop'].split(':')]
    sc = max(W / cw, H / ch)
    sw, sh = math.ceil(cw * sc / 2) * 2, math.ceil(ch * sc / 2) * 2
    ox = (sw - W) // 2
    oy = int(round((sh - H) * VBIAS.get(s['id'], 0.5)))
    vf = [f"select='between(round(t*{FPS})\\,{p['a']}\\,{p['b']})'",
          f"setpts=N*1001/24000/TB",
          "crop=1280:536:0:92", "pad=1280:540:0:4", "deblock=filter=strong:block=8",
          "crop=1280:536:0:4", f"crop={cw}:{ch}:{cx}:{cy-92}"]
    if p['mi']:
        # 2 cloned tail frames: minterpolate drops output at EOF; clones keep the tail inside this trailer shot
        vf.append("tpad=stop=2:stop_mode=clone")
        vf.append("minterpolate=fps=75:mi_mode=mci:mc_mode=aobmc:vsbmc=1:scd=none")
    sel = '+'.join(f'eq(n\\,{k})' for k in p['picks'])
    vf += [f"select='{sel}'", "setpts=N/25/TB",
           f"scale={sw}:{sh}:flags=lanczos+accurate_rnd+full_chroma_int", f"crop={W}:{H}:{ox}:{oy}",
           "unsharp=5:5:0.4", "format=yuv444p"]
    t0 = max(0, p['a'] / FPS - 1.0)
    out = f"{OUT}/plates/{s['id']}.mp4"
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-copyts', '-ss', f'{t0:.4f}', '-i', f'{PRJ}/source/trailer.mp4',
           '-an', '-vf', ','.join(vf), '-r', '25', '-frames:v', str(p['n']), '-c:v', 'libx264', '-preset', 'slow',
           '-crf', '10', '-pix_fmt', 'yuv444p', '-tune', 'film', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    return p, dict(crop_full=s['crop'], scale=f'{sw}x{sh}', cover_crop=f'{W}:{H}:{ox}:{oy}'), out

if __name__ == '__main__':
    ids = sys.argv[1:]
    edl = []
    for s in cues['shots']:
        if not s['id'].startswith('A') or (ids and s['id'] not in ids): continue
        p, g, out = build(s)
        print(s['id'], 'done', flush=True)
        edl.append({'id': s['id'], 'file': os.path.relpath(out, PRJ), 'f_in': s['f_in'], 'f_out': s['f_out'],
                    'frames': p['n'], 'src_in': s['src_in'], 'src_out': s['src_out'],
                    'speed': round(p['speed'], 4), 'speed_applied': round(p['eff_speed'], 4),
                    'speed_clamped_to_cut': p['clamped'],
                    'retime': 'minterpolate 75fps mci/aobmc/vsbmc, frame-picked' if p['mi'] else 'nearest source frame (no duplicates)',
                    'trailer_frames': [p['a'], p['b']], 'lib_shot': p['lib']['id'],
                    'lib_range': [p['lib']['in_frame'], p['lib']['out_frame']],
                    'characters': s['characters'], 'layer': s['layer'], **g})
    if not ids:
        json.dump({'project': 'sukanya-v2', 'editor': 'A (roster)', 'timing_source': 'shots/sh010/director/v001/cues.json',
                   'fps': 25, 'size': f'{W}x{H}', 'graded': False,
                   'codec': 'H.264 crf 10 yuv444p', 'prep': 'active crop -> pad 4 rows top -> deblock strong/8 -> crop back -> shot crop -> retime -> lanczos cover -> unsharp 5:5:0.4',
                   'f_out': 'exclusive', 'shots': edl}, open(f'{OUT}/edl_A.json', 'w'), indent=1)
