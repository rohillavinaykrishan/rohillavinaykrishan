import numpy as np, soundfile as sf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
tr,sr=sf.read('../../director/v001/audio/trailer_48k.wav'); bed,_=sf.read('../../director/v001/audio/bed_vinay30_v001.wav')
def env(x,t0,t1):
    a=x[int(t0*sr):int(t1*sr)].mean(1); b=int(.002*sr); a=a[:len(a)//b*b].reshape(-1,b)
    return np.arange(len(a))*.002+t0, 20*np.log10(np.sqrt((a**2).mean(1))+1e-9)
rows=[('S1 out src 73.35',tr,73.15,73.55,73.35),('S2 in src 122.825',tr,122.7,123.0,122.825),('bed join1 9.475',bed,9.3,9.7,9.475),
      ('S2 out src 127.62',tr,127.4,127.8,127.62),('S3 in src 104.88',tr,104.8,105.3,104.88),('bed join2 14.27 (hit 14.594)',bed,14.1,14.7,14.27),
      ('S3 out src 109.995',tr,109.8,110.2,109.995),('S4 in src 145.925',tr,145.85,146.1,145.925),('bed join3 19.385',bed,19.2,19.6,19.385)]
fig,ax=plt.subplots(3,3,figsize=(18,9))
for a,(n,x,t0,t1,c) in zip(ax.flat,rows):
    t,e=env(x,t0,t1); a.plot(t,e); a.axvline(c,c='r'); a.set_title(n); a.set_ylim(-70,0)
fig.tight_layout(); fig.savefig('work/zoom.png',dpi=65)
