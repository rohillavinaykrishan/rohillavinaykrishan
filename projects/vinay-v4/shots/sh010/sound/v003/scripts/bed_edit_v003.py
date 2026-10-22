# v003 bed: as v002, but the 117.38-118.68 gap is the REAL bed's own reverb decay (convolution of bed 117.10-117.38
# with a damped-noise reverb IR), decaying to ~-45 dBFS by 118.40 and ~-55..-60 by 118.68; crossfaded out 118.68-118.70
# while the untouched bed returns (20 ms raised cosine), so t >= 6.60 (src 118.70) is bit-identical to the bed.
import sys,numpy as np,soundfile as sf
from scipy.signal import fftconvolve,stft,istft
inp,out,rt_low=sys.argv[1],sys.argv[2],float(sys.argv[3]); match_db=float(sys.argv[4]) if len(sys.argv)>4 else -2.0
x,sr=sf.read(inp); x=x[:720000]; assert sr==48000 and len(x)==720000
t=np.arange(720000)/sr
def rc(a,b): return 0.5-0.5*np.cos(np.pi*np.clip((t-a)/(b-a),0,1))
fade_in=np.clip(t/0.12,0,1); tail=np.clip((14.00-t)/0.60,0,1)
dry_out=1-rc(5.20,5.28)                                   # 117.30 -> 117.38
bed_back=np.where(t<6.58,0.0,rc(6.58,6.60))               # returns, =1 from 6.60
dry=np.where(t<6.58,dry_out,bed_back)
# reverb input: bed 117.10-117.38 (t 5.00-5.28), 20 ms ramp-in at 5.00, then the same fade-out shape
w_in=rc(5.00,5.02)*dry_out*(t<5.28)
src=x*w_in[:,None]
# IR: stereo decorrelated noise, frequency-dependent RT60 (HF decays faster), shaped in STFT domain
rng=np.random.default_rng(173); L=int(3.0*sr); nper=1024
ir=[]
for ch in range(2):
    n=rng.standard_normal(L)
    f,tt,Z=stft(n,fs=sr,nperseg=nper)
    rt=rt_low*np.clip(1-0.55*np.log2(np.maximum(f,250)/250)/5,0.45,1.0)   # 250 Hz: rt_low ... 8 kHz: 0.45*rt_low
    env=10**(-3*tt[None,:]/rt[:,None])                                   # -60 dB at rt
    env*=np.clip(tt/0.01,0,1)[None,:]
    _,y=istft(Z*env,fs=sr,nperseg=nper); ir.append(y[:L])
ir=np.array(ir).T; ir/=np.sqrt((ir**2).sum(0,keepdims=True))
wet=np.stack([fftconvolve(src[:,c],ir[:,c])[:720000] for c in range(2)],1)
# level-match: wet RMS over 5.28-5.33 = dry RMS over 5.15-5.20 + match_db
def rms(a,t0,t1): s=slice(int(t0*sr),int(t1*sr)); return np.sqrt(np.mean(a[s]**2))
wet*=rms(x,5.15,5.20)/rms(wet,5.28,5.33)*10**(match_db/20)
w_wet=rc(5.20,5.28)*np.where(t<6.58,1.0,1-rc(6.58,6.60))
y=x*(dry*fade_in*tail)[:,None]+wet*w_wet[:,None]
sf.write(out,y,sr,subtype='FLOAT')
db=lambda a,b: 20*np.log10(rms(y,a,b)+1e-12)
print(f"rt_low {rt_low}: dBFS 5.15-5.20 {db(5.15,5.20):.1f} | 5.28-5.33 {db(5.28,5.33):.1f} | 5.6 {db(5.58,5.62):.1f} | 6.0 {db(5.98,6.02):.1f} | 6.30 (118.40) {db(6.28,6.32):.1f} | 6.55 {db(6.53,6.57):.1f} | 6.60-6.70 {db(6.60,6.70):.1f}  min|y| 5.3-6.58 {20*np.log10(np.abs(y[int(5.3*sr):int(6.58*sr)]).max()):.1f}dB peak")
print('identical to bed from 6.60 to 13.40:',bool(np.array_equal(y[int(6.60*sr):int(13.40*sr)],x[int(6.60*sr):int(13.40*sr)])))
