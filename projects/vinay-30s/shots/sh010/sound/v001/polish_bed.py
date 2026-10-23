# Sound v001: rebuilds the director's bed from trailer_48k.wav with the SAME segment timing (bed_segments.json),
# per-join equal-power crossfades centred on the beat-locked splice, head fade, tail fade ending at src 156.525.
# usage: vfx-python polish_bed.py out.wav XF1_ms XF2_ms XF3_ms [head_ms] [tail_s] [src_shift_ms per segment, e.g. 0,0,-10,0]
# src_shift < 0 takes the segment earlier in the source = its content lands later in the master (master splice points never move).
import sys, json, numpy as np, soundfile as sf
A='../../director/v001/audio/'
y, sr = sf.read(A+'trailer_48k.wav'); assert sr == 48000
segs = json.load(open(A+'bed_segments.json'))
xfs = [float(v)/1000 for v in sys.argv[2:5]]
head = float(sys.argv[5])/1000 if len(sys.argv) > 5 else 0.004
tail = float(sys.argv[6]) if len(sys.argv) > 6 else 0.6
shift = [float(v)/1000 for v in sys.argv[7].split(',')] if len(sys.argv) > 7 else [0, 0, 0, 0]
N = int(30.0*sr); out = np.zeros((N, 2))
for i, s in enumerate(segs):
    m0 = int(round(s['master_in_s']*sr)); a = s['src_in'] + shift[i]
    m1 = int(round(segs[i+1]['master_in_s']*sr)) if i < 3 else N
    hin = int(round(xfs[i-1]*sr/2)) if i > 0 else 0      # half crossfade before the splice
    hout = int(round(xfs[i]*sr/2)) if i < 3 else 0        # half crossfade after the next splice
    s0 = int(round(a*sr)) - hin
    seg = y[s0:s0 + (m1 - m0) + hin + hout].copy()
    g = np.ones(len(seg))
    if hin: g[:2*hin] *= np.sin(np.linspace(0, np.pi/2, 2*hin))
    if hout: g[-2*hout:] *= np.cos(np.linspace(0, np.pi/2, 2*hout))
    out[m0-hin:m0-hin+len(seg)] += seg*g[:, None]
h = int(head*sr); out[:h] *= np.sin(np.linspace(0, np.pi/2, h))[:, None]
end = N - int(round((156.54-156.525)*sr))            # src 156.525 = last allowed source sample
out[end:] = 0; t = int(tail*sr); out[end-t:end] *= np.cos(np.linspace(0, np.pi/2, t))[:, None]
sf.write(sys.argv[1], out, sr, subtype='PCM_24'); print('wrote', sys.argv[1], len(out)/sr, 's', 'xf', xfs, 'head', head, 'tail', tail)
