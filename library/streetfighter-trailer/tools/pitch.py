import numpy as np, librosa, json, sys
S=sys.argv[1]
y,sr=librosa.load(S+'/a22.wav',sr=22050)
spans=json.load(open(sys.argv[2]))
res=[]
for a,b in spans:
    seg=y[int(a*sr):int(b*sr)]
    f0,vf,vp=librosa.pyin(seg,fmin=80,fmax=800,sr=sr,frame_length=2048,hop_length=256)
    st=12*np.log2(f0/440.0)
    voiced=np.isfinite(st); vfrac=float(voiced.mean())
    # stable runs: consecutive voiced frames with |delta| < 0.35 semitone
    hop=256/sr; run=0; stable=0; runs=[]
    for i in range(1,len(st)):
        if voiced[i] and voiced[i-1] and abs(st[i]-st[i-1])<0.35: run+=1
        else:
            if run*hop>=0.12: stable+=run; runs.append(run*hop)
            run=0
    if run*hop>=0.12: stable+=run; runs.append(run*hop)
    sfrac=float(stable/max(1,voiced.sum()))
    res.append(dict(start=a,end=b,voiced_frac=round(vfrac,2),stable_frac=round(sfrac,2),longest_note_s=round(max(runs) if runs else 0,2),
                    pitch_range_st=round(float(np.nanpercentile(st,90)-np.nanpercentile(st,10)),1) if voiced.any() else None))
    print(res[-1])
json.dump(res,open(sys.argv[3],'w'))
