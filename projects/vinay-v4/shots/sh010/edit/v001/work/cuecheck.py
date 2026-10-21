import json, numpy as np, soundfile as sf, librosa, sys
y, sr = sf.read(sys.argv[1]); y = y.mean(1) if y.ndim > 1 else y
cues = json.load(open(sys.argv[2]))
hop = sr // 25
nf = len(y) // hop
rms = np.array([np.sqrt(np.mean(y[i*hop:(i+1)*hop]**2) + 1e-12) for i in range(nf)]); db = 20*np.log10(rms)
# onset strength at 25 fps-ish resolution (hop 480 @48k = 10 ms) then per-frame max
oh = 480; on = librosa.onset.onset_strength(y=y.astype(np.float32), sr=sr, hop_length=oh)
onf = np.array([on[i*4:(i+1)*4].max() if i*4 < len(on) else 0 for i in range(nf)])
ont = librosa.onset.onset_detect(onset_envelope=on, sr=sr, hop_length=oh, units='time', backtrack=False)
pk = np.percentile(onf, 90)
print('frames', nf, 'onset p90', round(pk, 2))
res = {}
for k, v in cues['music_hits'].items():
    fs = v['f'] if isinstance(v['f'], list) else [v['f']]
    for f in fs:
        exp_src = round(112.10 + f/25, 3)
        near = [round((t*25), 2) for t in ont if abs(t*25 - f) <= 3]
        lo, hi = max(0, f-3), min(nf, f+4)
        loc = int(lo + np.argmax(onf[lo:hi]))
        print(f"{k:14s} f{f:3d} src {v['src'] if not isinstance(v['src'], list) else v['src']} exp {exp_src}  rms {db[f]:6.1f} dB  d(prev) {db[f]-db[f-1]:+5.1f}  onset {onf[f]:5.2f} ({onf[f]/pk:4.1f}x p90)  local-onset-peak f{loc}  detected onsets(frames) {near}")
        res[f"{k}@{f}"] = dict(f=f, rms_db=round(float(db[f]), 1), d_db=round(float(db[f]-db[f-1]), 1), onset_x_p90=round(float(onf[f]/pk), 2), peak_f=loc, detected=near)
# overall rankings
top = np.argsort(onf)[::-1][:20]; print('top-20 onset frames', sorted(int(t) for t in top))
jumps = np.argsort(np.diff(db))[::-1][:10] + 1; print('top-10 rms jumps', [(int(f), round(float(db[f]-db[f-1]), 1)) for f in jumps])
loud = np.argsort(db)[::-1][:10]; print('loudest frames', [(int(f), round(float(db[f]), 1)) for f in loud])
print('quiet frames (< -28 dB)', [int(f) for f in np.nonzero(db < -28)[0]])
print('db 155-176', [round(float(x), 1) for x in db[155:177]])
print('db 0-8', [round(float(x), 1) for x in db[0:9]], 'db 355-374', [round(float(x), 1) for x in db[355:375]])
json.dump(dict(db=[round(float(x), 2) for x in db], onset=[round(float(x), 3) for x in onf], onsets_t=[round(float(t), 3) for t in ont], cues=res), open(sys.argv[3], 'w'))
