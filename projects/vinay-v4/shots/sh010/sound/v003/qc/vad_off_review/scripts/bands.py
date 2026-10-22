import sys,numpy as np,soundfile as sf
from scipy.signal import butter,sosfiltfilt
d='/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad/'
files=[('original',d+'bed_soxr_raw.wav'),('A rep_1.0_1.0_0.5 (passes)',d+'nv/rep_1.0_1.0_0.5_0.06.wav'),('B r4 floor-20',d+'nv/r4_0.5_-20.wav'),('C pc 70/95',d+'nv/pc_70_95_0.wav')]
bands=[('low <250',None,250),('mid 250-2.5k',250,2500),('high 2.5-9k',2500,9000)]
for n,f in files:
    x,sr=sf.read(f); x=x[:720000]; m=(x[:,0]+x[:,1])/2; L=x[:,0]
    row=[]
    for bn,lo,hi in bands:
        sos=butter(4,[lo,hi],'band',fs=sr,output='sos') if lo else butter(4,hi,'low',fs=sr,output='sos')
        for sig,sn in [(m,'mono'),(L,'L')]:
            y=sosfiltfilt(sos,sig); r=lambda a,b:10*np.log10(np.mean(y[int(a*sr):int(b*sr)]**2))
            ctx=(r(8.25,8.85)+r(10.45,11.0))/2; row.append(f"{bn} {sn}: span {r(9.0,10.3)-ctx:+5.1f}")
    print(f"{n:28s} | "+" | ".join(row))
print('(dB of span 9.0-10.3 relative to neighbouring music 8.25-8.85 / 10.45-11.0)')
