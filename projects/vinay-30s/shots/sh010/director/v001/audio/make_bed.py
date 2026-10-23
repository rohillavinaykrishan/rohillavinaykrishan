# Builds the 30.0 s bed from 4 trailer sections. usage: vfx-python make_bed.py
# Segments (trailer seconds, in -> out). In-points sit ~15 ms before the onset so attacks are kept.
import numpy as np, soundfile as sf, json
SR=48000
y, sr = sf.read('trailer_48k.wav'); assert sr==SR
SEG=[("S1_bathhouse_build", 63.875, 73.350),
     ("S2_streetfighter_line", 122.825, 127.620),
     ("S3_silence_HIT", 104.880, 109.995),
     ("S4_chant_title", 145.925, None)]
TOTAL=30.0
xf=int(0.006*SR)  # 6 ms equal-power crossfade at each splice (click-free)
used=sum(b-a for _,a,b in SEG[:3]); s4len=TOTAL-used
SEG[3]=(SEG[3][0],SEG[3][1],SEG[3][1]+s4len)
out=np.zeros((0,2)); log=[]; t=0.0
for i,(n,a,b) in enumerate(SEG):
    seg=y[int(round(a*SR)):int(round(b*SR))+ (xf if i<3 else 0)].copy()
    if len(out)==0:
        f=int(0.004*SR); seg[:f]*=np.linspace(0,1,f)[:,None]; out=seg
    else:
        k=np.linspace(0,np.pi/2,xf)[:,None]
        tail=out[-xf:]*np.cos(k); head=seg[:xf]*np.sin(k)
        out=np.concatenate([out[:-xf], tail+head, seg[xf:]])
    log.append({"id":n,"src_in":a,"src_out":round(b,3),"master_in_s":round(t,3),"master_in_f":round(t*25,2)}); t+=b-a
n=int(TOTAL*SR); out=out[:n]
if len(out)<n: out=np.concatenate([out,np.zeros((n-len(out),2))])
fo=int(0.6*SR); out[-fo:]*=np.cos(np.linspace(0,np.pi/2,fo))[:,None]  # 0.6 s equal-power tail fade (src 155.94-156.54)
sf.write('bed_vinay30_v001.wav', out, SR, subtype='PCM_24')
json.dump(log, open('bed_segments.json','w'), indent=1); print(json.dumps(log,indent=1)); print('len', len(out)/SR)
