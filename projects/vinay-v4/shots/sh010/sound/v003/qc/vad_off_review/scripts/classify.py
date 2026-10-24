import numpy as np,soundfile as sf,librosa,matplotlib,json; matplotlib.use('Agg'); import matplotlib.pyplot as plt
x,sr=sf.read('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/bed_soxr_raw.wav'); x=x[:720000]
M=(x[:,0]+x[:,1])/2; Sd=(x[:,0]-x[:,1])/2
nf=2048; hop=240
SM=librosa.stft(M,n_fft=nf,hop_length=hop); SS=librosa.stft(Sd,n_fft=nf,hop_length=hop)
mask=np.clip(1-np.abs(SS)/(np.abs(SM)+1e-9),0,1)**2
C=librosa.istft(SM*mask,hop_length=hop,length=len(M))
sf.write('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/nv/center.wav',C,sr)
print('mid/side energy ratio dB per span:')
for n,a,b in [('a 0-4',0,4),('b 3.8-5.2',3.8,5.2),('c 8.6-9.9',8.6,9.9),('ref 6.9-8.5 (no vocal?)',6.9,8.5),('ref 11-13',11,13)]:
    s=slice(int(a*sr),int(b*sr)); print(f'  {n:24s} M/S {10*np.log10(np.sum(M[s]**2)/np.sum(Sd[s]**2)):5.1f} dB')
y16=librosa.resample(C,orig_sr=sr,target_sr=16000)
f0,vf,vp=librosa.pyin(y16,fmin=80,fmax=900,sr=16000,frame_length=1024,hop_length=160)
tt=librosa.times_like(f0,sr=16000,hop_length=160)
tun=librosa.estimate_tuning(y=y16,sr=16000); print('tuning offset (fraction of semitone):',round(float(tun),3))
midi=librosa.hz_to_midi(f0)-tun
out={}
for n,a,b in [('a',0,4),('b',3.8,5.2),('c',8.6,9.9)]:
    s=(tt>=a)&(tt<b)&vf; m=midi[s]
    if len(m)<5: out[n]='too few voiced'; continue
    dev=np.abs(m-np.round(m))   # semitones from nearest note
    sl=np.abs(np.diff(midi[(tt>=a)&(tt<b)]))*100  # semitone/s  (10ms frames)
    sl=sl[np.isfinite(sl)]
    # plateau: runs >=8 frames (80 ms) where pitch stays within +-0.35 st of its run median
    vm=np.where((tt>=a)&(tt<b)&vf,midi,np.nan); runs=[];cur=[]
    for v in vm:
        if np.isfinite(v) and (not cur or abs(v-np.median(cur))<0.35): cur.append(v)
        else:
            if len(cur)>=8: runs.append(len(cur))
            cur=[v] if np.isfinite(v) else []
    if len(cur)>=8: runs.append(len(cur))
    out[n]=dict(voiced_frac=round(float(s.sum()/((tt>=a)&(tt<b)).sum()),2),median_cents_off_note=round(float(np.median(dev)*100),1),
        frac_within_25c=round(float((dev<0.25).mean()),2),median_slope_st_per_s=round(float(np.median(sl)),1),
        plateau_frames_frac=round(float(sum(runs)/max(1,s.sum())),2),n_plateaus=len(runs),notes=sorted(set(librosa.midi_to_note(np.round(m[dev<0.25]).astype(int)).tolist()))[:12])
    print(n,out[n])
fig,ax=plt.subplots(3,1,figsize=(22,13))
for a_,(n,a,b) in zip(ax,[('a 0-4',0,4.2),('b 3.8-5.2',3.6,5.4),('c 8.6-9.9',8.2,10.4)]):
    s=slice(int(a*sr/hop),int(b*sr/hop)); D=librosa.amplitude_to_db(np.abs(SM*mask)[:,s],ref=np.max(np.abs(SM)))
    fr=librosa.fft_frequencies(sr=sr,n_fft=nf); k=fr<=3000
    a_.pcolormesh(np.arange(s.start,s.stop)*hop/sr,fr[k],D[k],vmin=-80,vmax=0,shading='auto',cmap='magma')
    q=(tt>=a)&(tt<b); a_.plot(tt[q],f0[q],'c.',ms=3,label='pYIN f0 (centre-extracted)')
    for mm in range(43,80): a_.axhline(librosa.midi_to_hz(mm+tun),color='w',lw=0.2,alpha=0.4)
    a_.set_yscale('log'); a_.set_ylim(80,3000); a_.set_title(f'{n}: centre-extracted mid, narrowband; white lines = semitone grid (tuned)',loc='left'); a_.legend(loc='upper right')
    a_.set_xticks(np.arange(round(a,1),b,0.1)); a_.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/nv/classify.png',dpi=65)
json.dump(out,open('/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/nv/classify.json','w'),indent=1)
