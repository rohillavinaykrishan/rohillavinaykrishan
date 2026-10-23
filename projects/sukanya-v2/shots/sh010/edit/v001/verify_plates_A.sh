#!/bin/bash
# Verify A plates: ffprobe frame count/size/fps/pix_fmt vs cues.json, and per-frame luma diff
# (YDIF from signalstats on the frame difference) to flag duplicates (~0) or cuts (spike).
D=/home/user/rohillavinaykrishan/projects/sukanya-v2/shots/sh010
python3 - "$D" <<'PY'
import json,subprocess,sys
D=sys.argv[1]
c=json.load(open(f'{D}/director/v001/cues.json'))
ok=True
for s in c['shots']:
    if not s['id'].startswith('A'): continue
    f=f"{D}/edit/v001/plates/{s['id']}.mp4"; want=s['f_out']-s['f_in']
    r=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries',
      'stream=width,height,r_frame_rate,pix_fmt,nb_read_frames,codec_name','-of','json',f],capture_output=True,text=True)
    st=json.loads(r.stdout)['streams'][0]
    y=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',f,'-vf','scale=540:-2,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-',
      '-f','null','-'],capture_output=True,text=True).stdout
    d=[float(l.split('=')[1]) for l in y.splitlines() if 'YAVG' in l]
    good=(st['width'],st['height'],st['r_frame_rate'],st['pix_fmt'],int(st['nb_read_frames']))==(2160,1180,'25/1','yuv444p',want)
    ok&=good
    med=sorted(d)[len(d)//2] if d else 0
    print(f"{s['id']} {st['codec_name']} {st['width']}x{st['height']} {st['r_frame_rate']} {st['pix_fmt']} frames={st['nb_read_frames']}/{want} {'OK' if good else 'FAIL'} "
          f"diff min={min(d) if d else 0:.2f} med={med:.2f} max={max(d) if d else 0:.2f}")
print('ALL OK' if ok else 'FAILURES')
PY
