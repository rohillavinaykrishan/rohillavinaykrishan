#!/usr/bin/env python3
"""Verify plates (ffprobe frame counts/size/fps/pix_fmt, trailer-cut containment via shots.json,
hidden-cut scan inside every used source range) and write edl.json.  usage: python3 -I verify_plates.py"""
import json, subprocess, sys
import numpy as np
sys.path.insert(0, '/home/user/rohillavinaykrishan/projects/vinay-30s/shots/sh010/edit/v001')
import build_plates as b

lib = {s['id']: s for s in json.load(open(b.LIB))['shots']}
log = json.load(open(b.OUT + '/build_log.json'))
by_frame = sorted(lib.values(), key=lambda s: s['in_frame'])


def probe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height,r_frame_rate,pix_fmt,nb_read_frames,codec_name', '-of', 'json', p],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)['streams'][0]


def cut_scan(a, z):
    """mean abs luma diff between consecutive source frames a..z (160x67 luma)."""
    ss = max(0, a - 30)
    vf = ('select=between(n\\,%d\\,%d),crop=1280:536:0:92,scale=160:67,format=gray' % (a - ss, z - ss))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.6f' % ((ss - 0.5) / float(b.FPS_S)) if ss else '0',
                          '-i', b.SRC, '-vf', vf, '-vsync', '0', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 67, 160).astype(np.float32)
    d = [float(np.abs(fr[i + 1] - fr[i]).mean()) for i in range(len(fr) - 1)]
    return d


edl = {'project': 'vinay-30s', 'fps': 25, 'source': 'source/trailer.mp4 (23.976 fps, 1280x720)',
       'timing_source': 'shots/sh010/director/v001/cues.json',
       'prep': 'crop=1280:536:0:92,pad=1280:540:0:4,deblock=filter=strong:block=8,crop=1280:536:0:4,'
               'crop=<window>, retime, scale lanczos, unsharp 5:5:0.4 (tiles 0.25), H.264 crf10 yuv420p bt709',
       'cuts': []}
bad = 0
for it in b.items():
    i = it['id']; L = lib[it['lib']]; r = log[i]
    p = '%s/plates/%s.mp4' % (b.OUT, i)
    pr = probe(p)
    ow, oh = b.WIN[it['layer']]
    first, last = r['src_first_frame'], r['src_last_frame']
    # interpolation also reads one frame past the last position
    read_last = last + (1 if r['mode'] != 'map' else 0)
    inside = L['in_frame'] <= first and read_last <= L['out_frame']
    d = cut_scan(first, read_last)
    med = float(np.median(d)) if d else 0
    jumps = [first + k for k, v in enumerate(d) if v > max(25, 4 * med)]
    ok = (int(pr['nb_read_frames']) == it['frames'] and (pr['width'], pr['height']) == (ow, oh)
          and pr['r_frame_rate'] == '25/1' and pr['pix_fmt'] == 'yuv420p' and inside and not jumps)
    bad += not ok
    print('%-3s %-4s frames %s/%d %dx%d %s %s src %d-%d (lib %d-%d) inside=%s maxdiff=%.1f jumps=%s' % (
        'OK' if ok else 'BAD', i, pr['nb_read_frames'], it['frames'], pr['width'], pr['height'], pr['r_frame_rate'],
        pr['pix_fmt'], first, read_last, L['in_frame'], L['out_frame'], inside, max(d) if d else 0, jumps))
    edl['cuts'].append(dict(id=i, layer=it['layer'], file='shots/sh010/edit/v001/plates/%s.mp4' % i,
                            master_f_in=it['f_in'], master_f_out=it['f_out'], frames=it['frames'],
                            lib=it['lib'], lib_src_frames=[L['in_frame'], L['out_frame']],
                            cue_src_in=it['src_in'], cue_src_out=it['src_out'], src_in_used=r['src_in_actual'],
                            src_frames_used=[first, last], speed=it['speed'], retime=r['mode'], crop=it['crop'],
                            size='%dx%d' % (ow, oh), note=it['note']))
edl['cuts'][[c['id'] for c in edl['cuts']].index('H0')]['contact'] = {
    'src_frame': 1222, 'src_s': round(1222 * 1001 / 24000, 4), 'master_f': 365,
    'proof': 'shots/sh010/edit/v001/H0_contact_proof.png',
    'note': 'cue src_in 50.75 was a placeholder; contact = 50.9676. sf045 has 2 internal camera cuts the library '
            'missed (src 1216->1217 and 1221->1222); H0 starts exactly on the second one, so it crosses none'}
json.dump(edl, open(b.OUT + '/edl.json', 'w'), indent=1)
print('BAD:', bad)
