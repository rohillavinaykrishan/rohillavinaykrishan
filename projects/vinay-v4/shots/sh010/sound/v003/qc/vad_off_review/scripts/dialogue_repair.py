"""Remove a centred, pitched spoken line from the bed by spectral attenuation of the MID channel only.
gain(bin,frame) = 1 - depth * centre_mask * clip(harmonic_comb + cons_w*consonant_band(2.5-9k) + broad_w*band(250-5k)) * span_envelope
centre_mask = clip(1 - |S|/|M|, 0, 1)^2 (voice is centred). The side channel is untouched; nothing is added."""
import sys,numpy as np,soundfile as sf,librosa
from scipy.ndimage import maximum_filter1d,uniform_filter1d
inp,out,f0p=sys.argv[1:4]; A,B=float(sys.argv[4]),float(sys.argv[5]); depth=float(sys.argv[6]); cons_w=float(sys.argv[7]); broad_w=float(sys.argv[8]) if len(sys.argv)>8 else 0.0; bwf=float(sys.argv[9]) if len(sys.argv)>9 else 0.035
x,sr=sf.read(inp); M=(x[:,0]+x[:,1])/2; Sd=(x[:,0]-x[:,1])/2
nf=2048; hop=240
SM=librosa.stft(M,n_fft=nf,hop_length=hop); SS=librosa.stft(Sd,n_fft=nf,hop_length=hop)
fr=librosa.fft_frequencies(sr=sr,n_fft=nf); ft=librosa.frames_to_time(np.arange(SM.shape[1]),sr=sr,hop_length=hop)
cm=np.clip(1-np.abs(SS)/(np.abs(SM)+1e-9),0,1)**2
tt,f0,vp=np.load(f0p)
# f0 per STFT frame: nearest-valid hold within 150 ms, only inside [A,B]
valid=f0>0; f0f=np.zeros(len(ft))
for i,t in enumerate(ft):
    if A<=t<=B:
        d=np.abs(tt-t); d[~valid]=9; j=np.argmin(d)
        if d[j]<=0.15: f0f[i]=f0[j]
comb=np.zeros_like(cm)
for i,f in enumerate(f0f):
    if f<=0: continue
    for k in range(1,40):
        h=k*f
        if h>7000: break
        bw=max(35.0,bwf*h)                  # +-Hz
        comb[:,i]=np.maximum(comb[:,i],np.exp(-0.5*((fr-h)/(bw/1.5))**2))
comb=maximum_filter1d(comb,5,axis=1)          # +-2 frames (10 ms) time dilation
cons=((fr>=2500)&(fr<=9000)).astype(float)[:,None]*np.ones((1,len(ft)))
env=np.clip(np.minimum((ft-(A-0.04))/0.04,((B+0.04)-ft)/0.04),0,1)[None,:]
broad=((fr>=250)&(fr<=5000)).astype(float)[:,None]*np.ones((1,len(ft)))
W=np.clip(comb+cons_w*cons+broad_w*broad,0,1)*env
W=uniform_filter1d(W,3,axis=0)
G=1-depth*cm*W
M2=librosa.istft(SM*G,hop_length=hop,length=len(M))
# only replace inside the span (+ramps); elsewhere bit-identical
t=np.arange(len(M))/sr; w=np.clip(np.minimum((t-(A-0.06))/0.02,((B+0.06)-t)/0.02),0,1)
Mo=M*(1-w)+M2*w
y=np.stack([Mo+Sd,Mo-Sd],1)
sf.write(out,y,sr,subtype='FLOAT')
s=slice(int((A-0.05)*sr),int((B+0.05)*sr))
print(f'span {A}-{B}: level change {20*np.log10(np.sqrt(np.mean(y[s]**2))/np.sqrt(np.mean(x[s]**2))):+.2f} dB; mid {20*np.log10(np.sqrt(np.mean(Mo[s]**2))/np.sqrt(np.mean(M[s]**2))):+.2f} dB; max diff outside span',np.abs(y-x)[(t<A-0.07)|(t>B+0.07)].max())
