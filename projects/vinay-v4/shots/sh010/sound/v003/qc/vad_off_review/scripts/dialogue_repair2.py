"""Remove a centred spoken line from the bed: MID channel only, side untouched, nothing added.
Mid STFT is split (HPSS) into harmonic Hm and percussive Pm.
  Hm gain = max(floor, 1 - cm * act * clip(comb + broad_w*[250-5k]))      (voiced speech lives here)
  Pm gain = max(floor, 1 - cm * act * cons_w*[2.5-9k])                     (consonants; drum hits kept outside speech)
cm = centre mask clip(1-|S|/|M|,0,1)^2; act = speech activity (voiced frames +-pad, smoothed); comb = harmonics of tracked f0.
usage: in out f0.npy A B broad_w cons_w floor_db pad_s bwf [p_full 0|1] [protect t0:t1]
  p_full=1: Pm gets the same comb+broad+consonant weighting as Hm (needed: syllable onsets live in Pm)"""
import sys,numpy as np,soundfile as sf,librosa
from scipy.ndimage import maximum_filter1d,uniform_filter1d
inp,out,f0p=sys.argv[1:4]; A,B,broad_w,cons_w,floor_db,pad,bwf=map(float,sys.argv[4:11])
p_full=int(sys.argv[11]) if len(sys.argv)>11 else 0; prot=[float(v) for v in sys.argv[12].split(':')] if len(sys.argv)>12 else None
x,sr=sf.read(inp); M=(x[:,0]+x[:,1])/2; Sd=(x[:,0]-x[:,1])/2
nf=2048; hop=240
SM=librosa.stft(M,n_fft=nf,hop_length=hop); SS=librosa.stft(Sd,n_fft=nf,hop_length=hop)
Hm,Pm=librosa.decompose.hpss(SM,margin=1.0)
fr=librosa.fft_frequencies(sr=sr,n_fft=nf); ft=librosa.frames_to_time(np.arange(SM.shape[1]),sr=sr,hop_length=hop)
cm=np.clip(1-np.abs(SS)/(np.abs(SM)+1e-9),0,1)**2
tt,f0,vp=np.load(f0p); valid=f0>0
f0f=np.zeros(len(ft))
for i,t in enumerate(ft):
    if A<=t<=B:
        d=np.abs(tt-t); d[~valid]=9; j=np.argmin(d)
        if d[j]<=0.15: f0f[i]=f0[j]
act=(f0f>0).astype(float); pf=int(pad/(hop/sr)); act=maximum_filter1d(act,2*pf+1); act=uniform_filter1d(act,9)
inspan=((ft>=A)&(ft<=B)).astype(float); act*=inspan; act=uniform_filter1d(act,9)
comb=np.zeros_like(cm)
for i,f in enumerate(f0f):
    if f<=0: continue
    for k in range(1,40):
        h=k*f
        if h>7000: break
        bw=max(35.0,bwf*h); comb[:,i]=np.maximum(comb[:,i],np.exp(-0.5*((fr-h)/(bw/1.5))**2))
comb=maximum_filter1d(comb,5,axis=1)
band=lambda lo,hi:((fr>=lo)&(fr<=hi)).astype(float)[:,None]
fl=10**(floor_db/20)
GH=np.maximum(fl,1-cm*act[None,:]*np.clip(comb+broad_w*band(250,5000),0,1))
WP=np.clip(comb+broad_w*band(250,5000)+cons_w*band(2500,9000),0,1) if p_full else cons_w*band(2500,9000)
GP=np.maximum(fl,1-cm*act[None,:]*WP)
if prot:
    pw=np.clip(np.minimum((ft-prot[0])/0.01,(prot[1]-ft)/0.01),0,1)[None,:]   # protect the percussive attack of a picture cue hit
    GP=GP*(1-pw)+pw
GH=uniform_filter1d(GH,3,axis=0); GP=uniform_filter1d(GP,3,axis=0)
M2=librosa.istft(Hm*GH+Pm*GP,hop_length=hop,length=len(M))
t=np.arange(len(M))/sr; w=np.clip(np.minimum((t-(A-0.06))/0.02,((B+0.06)-t)/0.02),0,1)
Mo=M*(1-w)+M2*w; y=np.stack([Mo+Sd,Mo-Sd],1); sf.write(out,y,sr,subtype='FLOAT')
s=slice(int((A-0.05)*sr),int((B+0.05)*sr))
print(f'level change {20*np.log10(np.sqrt(np.mean(y[s]**2))/np.sqrt(np.mean(x[s]**2))):+.2f} dB; outside-span max diff {np.abs(y-x)[(t<A-0.07)|(t>B+0.07)].max()}; min gain H {20*np.log10(GH.min()):.1f} dB')
