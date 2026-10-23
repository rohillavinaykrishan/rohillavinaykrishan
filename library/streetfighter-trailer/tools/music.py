import numpy as np, librosa, json, sys, scipy.signal as ss
S=sys.argv[1]
y,sr=librosa.load(S+'/a22.wav',sr=22050); H=512; dur=len(y)/sr
rms=librosa.feature.rms(y=y,frame_length=2048,hop_length=H)[0]; db=20*np.log10(rms+1e-9)
t=librosa.frames_to_time(np.arange(len(rms)),sr=sr,hop_length=H)
oenv=librosa.onset.onset_strength(y=y,sr=sr,hop_length=H)
on=librosa.onset.onset_detect(onset_envelope=oenv,sr=sr,hop_length=H,backtrack=False,units='frames')
# silences: < -40 dBFS for >=0.12 s
sil=[];q=db<-40;i=0
while i<len(q):
    if q[i]:
        j=i
        while j<len(q) and q[j]: j+=1
        if t[min(j,len(t)-1)]-t[i]>=0.12: sil.append([round(float(t[i]),2),round(float(t[min(j,len(t)-1)]),2),round(float(db[i:j].min()),1)])
        i=j
    else: i+=1
# hits: onset strength x loudness, peaks >=0.8 s apart
score=oenv/oenv.max()*np.clip((db+60)/60,0,1)
pk,_=ss.find_peaks(score,distance=int(0.8*sr/H))
pk=pk[np.argsort(-score[pk])][:30]
hits=sorted([dict(t=round(float(t[p]),2),strength=round(float(score[p]),3),rms_db=round(float(db[p]),1)) for p in pk],key=lambda h:h['t'])
# sections: novelty on mfcc+chroma
mf=librosa.feature.mfcc(y=y,sr=sr,hop_length=H,n_mfcc=13); ch=librosa.feature.chroma_cqt(y=y,sr=sr,hop_length=H)
F=np.vstack([librosa.util.normalize(mf,axis=1),ch,db[None,:]/20])
# downsample to ~4 Hz
step=int(sr/H/4); Fd=np.stack([F[:,i:i+step].mean(1) for i in range(0,F.shape[1]-step,step)],1); td=np.arange(Fd.shape[1])*step*H/sr
Fd=(Fd-Fd.mean(1,keepdims=True))/(Fd.std(1,keepdims=True)+1e-6)
Sm=np.corrcoef(Fd.T); K=16
g=np.outer(np.r_[-np.ones(K),np.ones(K)],np.r_[-np.ones(K),np.ones(K)])*np.outer(ss.windows.gaussian(2*K,K/2),ss.windows.gaussian(2*K,K/2))
nov=np.zeros(len(td))
for i in range(K,len(td)-K): nov[i]=(Sm[i-K:i+K,i-K:i+K]*g).sum()
nov=np.maximum(nov,0); nov/=nov.max()
bp,_=ss.find_peaks(nov,distance=4*4,height=0.18)
bounds=[0.0]+[float(td[b]) for b in bp]+[dur]
secs=[]
for a,b in zip(bounds[:-1],bounds[1:]):
    m=(t>=a)&(t<b); seg=y[int(a*sr):int(b*sr)]
    tempo=float(np.atleast_1d(librosa.beat.beat_track(y=seg,sr=sr)[0])[0]) if b-a>4 else None
    secs.append(dict(start=round(a,2),end=round(b,2),rms_db_mean=round(float(db[m].mean()),1),rms_db_max=round(float(db[m].max()),1),
       onsets_per_s=round(float(((t[on]>=a)&(t[on]<b)).sum()/(b-a)),2),tempo_bpm=round(tempo,1) if tempo else None))
# 0.5 s rms curve
step2=int(0.5*sr/H)
curve=[[round(float(t[i]),1),round(float(db[i:i+step2].mean()),1)] for i in range(0,len(db),step2)]
json.dump(dict(duration=round(dur,3),rms_curve_0p5s=curve,onsets=[round(float(x),2) for x in t[on]],silences=sil,loudest_hits=hits,sections=secs,novelty_peaks=[round(float(td[b]),2) for b in bp]),open(S+'/music.json','w'))
print(len(on),'onsets',len(sil),'silences'); print(sil); print(hits); 
for s in secs: print(s)
