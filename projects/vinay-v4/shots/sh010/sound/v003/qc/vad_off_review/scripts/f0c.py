import numpy as np,soundfile as sf,librosa
C,sr=sf.read('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/nv/center.wav')
a,b=8.6,10.8; seg=C[int(a*sr):int(b*sr)]
f0,vf,vp=librosa.pyin(seg,fmin=250,fmax=1000,sr=sr,frame_length=4096,hop_length=480)
tt=a+np.arange(len(f0))*0.01
runs=[];cur=None
for t,v,f in zip(tt,vf,f0):
    if v and cur is None: cur=[t,t,[f]]
    elif v: cur[1]=t; cur[2].append(f)
    elif cur: runs.append(cur); cur=None
if cur: runs.append(cur)
for r in runs:
    if r[1]-r[0]>=0.04: print(f"voiced {r[0]:.2f}-{r[1]:.2f}  f0 {np.min(r[2]):.0f}-{np.max(r[2]):.0f} Hz median {np.median(r[2]):.0f}  ({librosa.hz_to_note(np.median(r[2]))})  range {12*np.log2(np.max(r[2])/np.min(r[2])):.1f} st")
np.save('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/nv/f0c.npy',np.stack([tt,np.where(vf,f0,0),vp]))
