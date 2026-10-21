import json,numpy as np,soundfile as sf,librosa
x,sr=sf.read('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/bed_raw.wav'); y=x.mean(1).astype(np.float32)
hop=240
oenv=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop,n_fft=1024)
ons=librosa.onset.onset_detect(onset_envelope=oenv,sr=sr,hop_length=hop,units='frames',backtrack=False,delta=0.15,wait=4)
ts=librosa.frames_to_time(ons,sr=sr,hop_length=hop); st=oenv[ons]/oenv.max()
rms=librosa.feature.rms(y=y,frame_length=960,hop_length=hop)[0]; rdb=20*np.log10(rms+1e-9)
h=json.load(open('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/meas.json'))['hits']
out={}
for k,v in h.items():
    t=v['t']; sel=[(round(float(a),3),round(float(s),2),round(float(rdb[int(a*sr/hop)+4]),1)) for a,s in zip(ts,st) if abs(a-t)<=0.13]
    print(f"{k:14s} t={t:5.2f}: "+"  ".join(f"{a:.3f}[{(a-t)*25:+.2f}f s={s} {d}dB]" for a,s,d in sel))
    out[k]=sel
json.dump(dict(onsets=[(round(float(a),3),round(float(s),3)) for a,s in zip(ts,st)],near=out),open('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/ons.json','w'))
