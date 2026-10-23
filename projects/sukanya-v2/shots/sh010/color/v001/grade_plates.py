#!/usr/bin/env python3
"""grade_plates.py - make graded copies of the editors' plates (colorist sh010 v001).

  edit/v001/plates/<ID>.mp4  ->  color/v001/plates/<ID>.mp4   (same size, same frame count)
LUT per cues.json layer:  roll_panel -> tritone.cube (+ luma grain before the LUT)
                          charge     -> drain.cube   (+ luma grain before the LUT)
                          super_band -> band_<ID>.cube (band look + the shot's own cast trim)
Encode: H.264 -crf 10, yuv444p, Rec.709 tags, tv range, no audio.

Usage: python3 grade_plates.py [IDs...]   (default: every plate present and not yet graded)
       python3 grade_plates.py --force B01
Writes chains.json (the exact ffmpeg -vf per plate) and runs qc_rgb.py on each output.
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(os.path.dirname(HERE))                 # shots/sh010
sys.path.insert(0, HERE)
import make_luts as ML                                      # noqa: E402

CUES = json.load(open(os.path.join(SH, 'director/v001/cues.json')))
SHOTS = {s['id']: s for s in CUES['shots']}
SRC = os.path.join(SH, 'edit/v001/plates')
DST = os.path.join(HERE, 'plates')
GRAIN = 'noise=c0s=7:c0f=t'                                 # treatment: noise=alls=7:allf=t, luma only so it stays on the ramp
ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '10', '-pix_fmt', 'yuv444p',
       '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
       '-an', '-movflags', '+faststart']


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries',
                          'stream=width,height,r_frame_rate,nb_read_packets,color_range', '-of', 'json', path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)['streams'][0]


def in_range(st):
    return 'pc' if st.get('color_range') == 'pc' else 'tv'


def chain(lut, grain, rng):
    pre = (GRAIN + ',') if grain else ''
    return (f"{pre}scale=in_color_matrix=bt709:in_range={rng}:out_range=pc,format=gbrp16le,"
            f"lut3d=file='{lut}':interp=tetrahedral,"
            f"scale=out_color_matrix=bt709:out_range=tv,format=yuv444p")


def plate_cast(path, step=2, scale=4):
    st = probe(path)
    w, h = int(st['width']) // scale, int(st['height']) // scale
    vf = (f"select='not(mod(n\\,{step}))',scale={w}:{h}:in_color_matrix=bt709:in_range={in_range(st)}"
          f":out_range=pc,format=rgb24")
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-vf', vf, '-fps_mode', 'passthrough',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3) / 255.0
    return ML.shot_cast(list(fr))


def grade(sid, force=False):
    shot = SHOTS[sid]
    src, dst = os.path.join(SRC, sid + '.mp4'), os.path.join(DST, sid + '.mp4')
    import time
    if not os.path.exists(src):
        return None
    if os.path.exists(dst) and not force and os.path.getmtime(dst) >= os.path.getmtime(src):
        return None                                          # up to date (re-grades if the editor re-delivers)
    if time.time() - os.path.getmtime(src) < 90:
        print(f'{sid}: source changed <90 s ago, still being written? skipped'); return None
    try:
        st = probe(src)
    except subprocess.CalledProcessError:
        print(f'{sid}: source not readable yet, skipped'); return None
    want = shot['f_out'] - shot['f_in']
    layer = shot['layer']
    info = dict(id=sid, layer=layer, src=src, frames_expected=want, frames_src=int(st['nb_read_packets']),
                size=f"{st['width']}x{st['height']}", fps=st['r_frame_rate'], src_range=in_range(st))
    if layer == 'roll_panel':
        lut, grain = os.path.join(HERE, 'tritone.cube'), True
    elif layer == 'charge':
        lut, grain = os.path.join(HERE, 'drain.cube'), True
    elif layer == 'super_band':
        cast = plate_cast(src)
        lut, grain = ML.write_band_shot(HERE, sid, cast), False
        info['cast_ab'] = [round(float(c), 5) for c in cast]
    else:
        raise SystemExit(f'{sid}: layer {layer} is not a plate')
    vf = chain(lut, grain, in_range(st))
    info['vf'] = vf
    info['lut'] = os.path.basename(lut)
    os.makedirs(DST, exist_ok=True)
    tmp = dst + '.part.mp4'
    subprocess.run(['nice', '-n', '5', 'ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', src, '-vf', vf,
                    '-fps_mode', 'passthrough', '-threads', '2'] + ENC + [tmp], check=True)
    os.replace(tmp, dst)
    so = probe(dst)
    info['frames_out'] = int(so['nb_read_packets'])
    info['size_out'] = f"{so['width']}x{so['height']}"
    info['frames_ok'] = info['frames_out'] == info['frames_src'] and info['size_out'] == info['size']
    q = subprocess.run([sys.executable, os.path.join(HERE, 'qc_rgb.py'), dst], capture_output=True, text=True)
    info['qc'] = q.stdout.strip()
    info['qc_pass'] = q.returncode == 0
    return info


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    ids = args or [s for s in SHOTS if os.path.exists(os.path.join(SRC, s + '.mp4'))]
    cj = os.path.join(HERE, 'chains.json')
    chains = json.load(open(cj)) if os.path.exists(cj) else {}
    for sid in ids:
        info = grade(sid, force)
        if info is None:
            continue
        chains[sid] = info
        json.dump(chains, open(cj, 'w'), indent=1)
        print(f"{sid}: {info['lut']} frames {info['frames_src']}->{info['frames_out']} (cues {info['frames_expected']}) "
              f"{'OK' if info['frames_ok'] else 'FRAME/SIZE MISMATCH'} | {info['qc']}")


if __name__ == '__main__':
    main()
