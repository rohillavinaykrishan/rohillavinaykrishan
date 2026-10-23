#!/usr/bin/env python3
"""Build ungraded plates for SPECTRUM from cues.json (the only timing source).

usage: python3 -I build_plates.py [ID ...]      (no IDs = all, in delivery order)
       python3 -I build_plates.py --edl         (only rewrite edl.json)

Pipeline per plate (all in yuv444p, no RGB round trip):
  decode trailer -> crop=1280:536:0:92 -> pad=1280:540:0:4 (grid realign, pad on TOP)
  -> deblock strong/8 -> crop=1280:536:0:4 -> crop window x
  -> retime (map | mci | blend | ramp) to exactly f_out-f_in frames (tiles 40)
  -> lanczos scale to the window size, unsharp -> H.264 crf 10 yuv420p 25 fps, bt709 tags.
Retime modes:
  map   : speed >= 0.9, frame mapping src_t = src_in + k/25*speed (floor), no interpolation
  mci   : minterpolate mci/aobmc at fps = 25/speed, one interpolated frame per output frame
  blend : linear frame-blend between neighbouring source frames (R7, per cues note)
  ramp  : C6, speed 1.0 -> 0.2 linear over the shot, mci at 250 fps then pick nearest
"""
import json, math, os, subprocess, sys
from fractions import Fraction
import numpy as np

ROOT = '/home/user/rohillavinaykrishan'
P = ROOT + '/projects/vinay-30s'
CUES = P + '/shots/sh010/director/v001/cues.json'
LIB = ROOT + '/library/streetfighter-trailer/shots.json'
SRC = P + '/source/trailer.mp4'
OUT = P + '/shots/sh010/edit/v001'
FPS_S = Fraction(24000, 1001)
EPS = 1e-6

# editor decisions (documented in notes.md / edl.json)
H0_CONTACT_FRAME = 1222          # sf045: first frame the glove is on Ken's face (H0_contact_proof.png)
MODE_OVERRIDE = {'R7': 'blend', 'C6': 'ramp'}
WIN = {'roster': (2160, 904), 'strike': (2160, 904), 'clash': (2160, 1206), 'tile': (482, 430)}
FALLBACK_BLEND = set(os.environ.get('BLEND', '').split(',')) - {''}   # ids forced to frame-blend


def items():
    c = json.load(open(CUES))
    out = []
    for s in c['shots']:
        out.append(dict(id=s['id'], layer=s['layer'], lib=s['lib'], f_in=s['f_in'], f_out=s['f_out'],
                        frames=s['frames'], src_in=s['src_in'], src_out=s['src_out'], speed=s['speed'],
                        crop=s['crop'], note=s.get('note', '')))
    for t in c['tiles']:
        out.append(dict(id=t['id'], layer='tile', lib=t['lib'], f_in=t['arrive_f'],
                        f_out=t['arrive_f'] + t['clip_frames'], frames=t['clip_frames'],
                        src_in=t['src_in'], src_out=t['src_out'], speed=t['speed'], crop=t['crop'],
                        note='freeze last frame from f%d' % t['freeze_from_f']))
    return out


def plan(it):
    """Return the retime plan: first src frame a, list of fractional src positions (relative to a)."""
    n = it['frames']
    mode = MODE_OVERRIDE.get(it['id'])
    if it['id'] in FALLBACK_BLEND:
        mode = 'blend'
    if mode is None:
        mode = 'map' if it['speed'] >= 0.9 else 'mci'
    if it['id'] == 'H0':
        t0 = float(H0_CONTACT_FRAME / FPS_S)
    else:
        t0 = it['src_in']
    sp = it['speed']
    if mode == 'ramp':
        # speed 1.0 -> 0.2 linear over n frames (avg 0.6), cumulative src time
        spd = [1.0 - 0.8 * k / (n - 1) for k in range(n)]
        tau = [0.0]
        for k in range(1, n):
            tau.append(tau[-1] + spd[k - 1] / 25.0)
    else:
        tau = [k * sp / 25.0 for k in range(n)]
    if mode in ('mci', 'ramp'):
        # snap the start to a real source frame so interpolation phase is exact
        a = int(math.floor(t0 * FPS_S + 0.5))
        pos = [float(x * FPS_S) for x in tau]
    else:
        a = int(math.floor(t0 * FPS_S + EPS))
        off = float(t0 * FPS_S) - a
        pos = [off + float(x * FPS_S) for x in tau]
    return mode, a, pos


def decode(it, a, count, extra_vf=''):
    w, h, x, y = [int(v) for v in it['crop'].split(':')]
    vf = ('setpts=N/(24000/1001)/TB,crop=1280:536:0:92,pad=1280:540:0:4,deblock=filter=strong:block=8,'
          'crop=1280:536:0:4,crop=%d:%d:%d:%d' % (w, h, x, y - 92))
    vf += ',trim=end_frame=%d' % count
    if extra_vf:
        vf += ',' + extra_vf
    ss = float((a - 0.5) / FPS_S)
    cmd = ['ffmpeg', '-v', 'error', '-threads', '2', '-ss', '%.6f' % ss, '-i', SRC, '-an', '-vf', vf,
           '-f', 'rawvideo', '-pix_fmt', 'yuv444p', '-']
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    fs = w * h * 3
    arr = np.frombuffer(raw, np.uint8)
    return arr.reshape(-1, 3, h, w), (w, h)


def encode(frames, wh, it, path):
    ow, oh = WIN[it['layer']]
    sharp = 'unsharp=5:5:0.25' if it['layer'] == 'tile' else 'unsharp=5:5:0.4'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'yuv444p', '-s', '%dx%d' % wh,
           '-r', '25', '-i', '-', '-vf', 'scale=%d:%d:flags=lanczos+accurate_rnd+full_chroma_int,%s,format=yuv420p'
           % (ow, oh, sharp), '-c:v', 'libx264', '-preset', 'slow', '-crf', '10', '-pix_fmt', 'yuv420p',
           '-threads', '2', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
           '-color_range', 'tv', '-r', '25', '-an', '-movflags', '+faststart', path]
    subprocess.run(cmd, input=np.ascontiguousarray(frames).tobytes(), check=True)


def build(it):
    mode, a, pos = plan(it)
    n = it['frames']
    last_src = a + int(math.ceil(pos[-1] + EPS))
    if mode == 'map':
        idx = [int(math.floor(p + EPS)) for p in pos]
        src, wh = decode(it, a, idx[-1] + 1)
        frames = src[idx]
        used = (a + idx[0], a + idx[-1])
    elif mode == 'blend':
        cnt = int(math.floor(pos[-1])) + 2
        src, wh = decode(it, a, cnt)
        out = []
        for p in pos:
            i = int(math.floor(p + EPS)); f = p - i
            if f < 1e-3 or i + 1 >= len(src):
                out.append(src[min(i, len(src) - 1)])
            else:
                out.append(np.clip((1 - f) * src[i].astype(np.float32) + f * src[i + 1].astype(np.float32) + 0.5,
                                   0, 255).astype(np.uint8))
        frames = np.stack(out)
        used = (a, a + int(math.ceil(pos[-1] - 1e-3)))
    else:
        if mode == 'mci':
            fr = Fraction(25) / Fraction(it['speed']).limit_denominator(1000)
            if it['id'] == 'R1':  # 0.833 in cues = 5/6 (src_in..src_out = 0.9 s over 27 f)
                fr = Fraction(30)
        else:
            fr = Fraction(250)
        cnt = int(math.ceil(pos[-1] + EPS)) + 2   # +1 frame after the last needed position
        mi = 'minterpolate=fps=%d/%d:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none' % (
            fr.numerator, fr.denominator)
        src, wh = decode(it, a, cnt, mi)
        # src[j] is at time j/fr after frame a
        idx = [int(round(float(p / FPS_S * fr))) for p in pos]
        if max(idx) >= len(src):
            raise SystemExit('%s: interpolated stream too short (%d < %d)' % (it['id'], len(src), max(idx) + 1))
        frames = src[idx]
        used = (a, a + int(math.ceil(pos[-1] - 1e-3)))
    if it['id'] == 'H0':
        # hybrid: mci ghosts on the 1222->1224 impact (glove doubles); hold contact 4 f, step 1223 for 2 f,
        # then 0.3x mci from 1224 (clean, small motion)
        hold, _ = decode(it, H0_CONTACT_FRAME, 2)
        rest = n - 6
        fr = Fraction(250, 3)
        mi = 'minterpolate=fps=250/3:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none'
        need = int(math.ceil(rest * 0.3 / 25 * float(FPS_S))) + 2
        tail, _ = decode(it, H0_CONTACT_FRAME + 2, need, mi)
        frames = np.concatenate([hold[[0, 0, 0, 0, 1, 1]], tail[:rest]])
        mode = 'hold4(1222)+hold2(1223)+mci0.3x(from1224)'
        used = (H0_CONTACT_FRAME, H0_CONTACT_FRAME + 2 + int(math.ceil((rest - 1) * 0.3 / 25 * float(FPS_S))))
    assert len(frames) == n, (it['id'], len(frames), n)
    path = '%s/plates/%s.mp4' % (OUT, it['id'])
    encode(frames, wh, it, path)
    return dict(mode=mode, src_first_frame=used[0], src_last_frame=used[1],
                src_in_actual=round(float(a / FPS_S) + (0 if mode in ('mci', 'ramp') else pos[0] / float(FPS_S)), 4))


def main():
    args = sys.argv[1:]
    its = items()
    order = ['H0'] + ['R%d' % i for i in range(1, 9)] + ['C%d' % i for i in range(1, 7)] + \
            ['F%d' % i for i in range(1, 10)] + ['T%d' % i for i in range(1, 9)]
    byid = {i['id']: i for i in its}
    logp = OUT + '/build_log.json'
    log = json.load(open(logp)) if os.path.exists(logp) else {}
    if args and args[0] != '--edl':
        todo = args
    elif args:
        todo = []
    else:
        todo = order
    for i in todo:
        r = build(byid[i])
        log[i] = r
        json.dump(log, open(logp, 'w'), indent=1)
        print(i, r, flush=True)


if __name__ == '__main__':
    main()
