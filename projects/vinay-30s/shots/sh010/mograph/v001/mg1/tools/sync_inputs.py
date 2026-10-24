#!/usr/bin/env python3
"""Pull the best available inputs into mg1/assets/mg1/ (run again whenever upstream lands).
Plates: color/v001/plates/<ID>.mp4 > edit/v001/plates/<ID>.mp4 > mg1/placeholder/<ID>.mp4
Kit:    mograph/v001/kit/kit.js -> assets/mg1/kit/kit.js
Also extracts the last frame of R1-R8 (wipe holds + spectrum shutter) and writes inputs.json."""
import json, os, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SH = os.path.abspath(os.path.join(ROOT, '../../..'))
cues = json.load(open(os.path.join(SH, 'director/v001/cues.json')))
A = os.path.join(ROOT, 'assets/mg1')
for d in ('plates', 'stills', 'kit'): os.makedirs(os.path.join(A, d), exist_ok=True)
import time
def ok(p):
    if not (os.path.exists(p) and os.path.getsize(p) > 0 and time.time() - os.path.getmtime(p) > 20): return False
    try: probe(p); return True
    except Exception: return False
def probe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries',
                        'stream=width,height,nb_read_frames,pix_fmt,r_frame_rate', '-of', 'json', p], capture_output=True, text=True)
    return json.loads(r.stdout)['streams'][0]
state_p = os.path.join(ROOT, 'inputs.json')
state = json.load(open(state_p)) if os.path.exists(state_p) else {}
out = {'plates': {}, 'kit': None}
for s in cues['shots']:
    if s['f_in'] >= 357: continue
    i = s['id']
    cands = [('color', os.path.join(SH, 'color/v001/plates', i + '.mp4')),
             ('edit', os.path.join(SH, 'edit/v001/plates', i + '.mp4')),
             ('placeholder', os.path.join(ROOT, 'placeholder', i + '.mp4'))]
    kind, src = next((k, p) for k, p in cands if ok(p))
    sig = [src, os.path.getsize(src), int(os.path.getmtime(src))]
    dst = os.path.join(A, 'plates', i + '.mp4')
    prev = state.get('plates', {}).get(i, {})
    if prev.get('sig') != sig or not os.path.exists(dst):
        info = probe(src)
        if info['pix_fmt'] != 'yuv420p' or info['r_frame_rate'] != '25/1':
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf', 'fps=25', '-pix_fmt', 'yuv420p',
                            '-c:v', 'libx264', '-crf', '12', '-an', dst], check=True)
        else:
            shutil.copyfile(src, dst)
        info = probe(dst)
        n = int(info['nb_read_frames'])
        if s['id'].startswith('R'):
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', dst, '-vf', f'select=eq(n\\,{n-1})',
                            '-frames:v', '1', '-q:v', '2', os.path.join(A, 'stills', i + '_last.jpg')], check=True)
        prev = {'sig': sig, 'kind': kind, 'src': os.path.relpath(src, SH), 'frames': n,
                'expected': s['frames'], 'size': f"{info['width']}x{info['height']}"}
        print('updated', i, kind, prev['size'], n, '/', s['frames'], '' if n == s['frames'] else '  FRAME COUNT MISMATCH')
    out['plates'][i] = prev
kit = os.path.join(SH, 'mograph/v001/kit/kit.js')
if os.path.exists(kit):
    shutil.copyfile(kit, os.path.join(A, 'kit/kit.js')); out['kit'] = {'src': os.path.relpath(kit, SH), 'mtime': int(os.path.getmtime(kit))}
json.dump(out, open(state_p, 'w'), indent=1)
print('kinds:', {k: v['kind'] for k, v in out['plates'].items()})
