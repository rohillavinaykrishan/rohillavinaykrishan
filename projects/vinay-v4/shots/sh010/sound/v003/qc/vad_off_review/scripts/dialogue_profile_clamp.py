"""Remove a centred spoken line sitting over continuous music, MID channel only (side untouched, nothing added).
Mid STFT -> HPSS (Hm, Pm). For each bin, the music's own level is profiled from neighbouring context (before/after the line):
  ref_H = percentile(|Hm|, qH) over context frames, ref_P = percentile(|Pm|, qP).
Inside the span, each component is clamped to its music profile: g = min(1, k*ref/|X|), weighted by the centre mask
(so wide/side-dominant content is kept), floored at floor_db, smoothed, with 40 ms ramps; bit-identical outside the span.
usage: in out A B ctx0a:ctx0b,ctx1a:ctx1b qH qP k_db floor_db"""
import sys,numpy as np,soundfile as sf,librosa
from scipy.ndimage import uniform_filter
inp,out=sys.argv[1:3]; A,B=float(sys.argv[3]),float(sys.argv[4]); ctx=[tuple(map(float,c.split(':'))) for c in sys.argv[5].split(',')]
qH,qP,k_db,floor_db=map(float,sys.argv[6:10])
x,sr=sf.read(inp); M=(x[:,0]+x[:,1])/2; Sd=(x[:,0]-x[:,1])/2
nf=2048; hop=240
SM=librosa.stft(M,n_fft=nf,hop_length=hop); SS=librosa.stft(Sd,n_fft=nf,hop_length=hop)
Hm,Pm=librosa.decompose.hpss(SM,margin=1.0)
ft=librosa.frames_to_time(np.arange(SM.shape[1]),sr=sr,hop_length=hop)
cm=np.clip(1-np.abs(SS)/(np.abs(SM)+1e-9),0,1)**2
cidx=np.zeros(len(ft),bool)
for a,b in ctx: cidx|=(ft>=a)&(ft<=b)
k=10**(k_db/20); fl=10**(floor_db/20)
def clamp(X,q):
    ref=np.percentile(np.abs(X[:,cidx]),q,axis=1)[:,None]
    g=np.minimum(1,k*ref/(np.abs(X)+1e-12)); g=np.maximum(g,fl)
    return uniform_filter(g,(3,3))
env=np.clip(np.minimum((ft-(A-0.04))/0.04,((B+0.04)-ft)/0.04),0,1)[None,:]
GH=1-env*cm*(1-clamp(Hm,qH)); GP=1-env*cm*(1-clamp(Pm,qP))
M2=librosa.istft(Hm*GH+Pm*GP,hop_length=hop,length=len(M))
t=np.arange(len(M))/sr; w=np.clip(np.minimum((t-(A-0.06))/0.02,((B+0.06)-t)/0.02),0,1)
Mo=M*(1-w)+M2*w; y=np.stack([Mo+Sd,Mo-Sd],1); sf.write(out,y,sr,subtype='FLOAT')
s=slice(int((A-0.05)*sr),int((B+0.05)*sr))
print(f'level change {20*np.log10(np.sqrt(np.mean(y[s]**2))/np.sqrt(np.mean(x[s]**2))):+.2f} dB; outside-span max diff {np.abs(y-x)[(t<A-0.07)|(t>B+0.07)].max()}')
