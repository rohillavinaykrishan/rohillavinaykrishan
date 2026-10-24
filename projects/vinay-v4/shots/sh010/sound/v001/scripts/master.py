import sys,numpy as np,soundfile as sf,subprocess,re
from scipy.signal import resample_poly
from scipy.ndimage import minimum_filter1d,uniform_filter1d
src,out,ceil_db,target=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4])
x,sr=sf.read(src); x=x[:720000]; assert sr==48000 and x.shape==(720000,2)
def tp(y): return 20*np.log10(np.abs(resample_poly(y,4,1,axis=0)).max())
def ebu(path):
    r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',path,'-af','ebur128=peak=true:framelog=quiet','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1]),float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',r)[-1])
def limit(y,c):
    up=np.abs(resample_poly(y,4,1,axis=0)).max(1)
    pk=up.reshape(-1,4).max(1)            # per-sample true-ish peak
    req=np.minimum(1.0,c/np.maximum(pk,1e-9))
    L=int(0.010*sr)                        # 10 ms
    g=minimum_filter1d(req,2*L+1,mode='nearest')
    g=uniform_filter1d(g,L,mode='nearest')
    g=np.minimum(g,minimum_filter1d(req,2*L+1,mode='nearest')*0+g)  # keep
    return y*g[:,None],g
c=10**(ceil_db/20); gain_db=target-(-14.4)
for it in range(6):
    y,g=limit(x*10**(gain_db/20),c)
    sf.write(out,y,sr,subtype='PCM_24')
    I,P=ebu(out)
    print(f"it{it} gain {gain_db:+.2f} dB -> I {I} LUFS, TP(ffmpeg) {P} dBTP, TP(4x) {tp(y):.2f}, max GR {-20*np.log10(g.min()):.2f} dB, samples limited {(g<0.999).sum()} ({(g<0.999).mean()*100:.2f}%)")
    if abs(I-target)<0.05: break
    gain_db+=target-I
