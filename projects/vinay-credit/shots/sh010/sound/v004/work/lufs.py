import sys, numpy as np, soundfile as sf, scipy.signal as ss
for f in sys.argv[1:]:
    y, sr = sf.read(f, dtype="float64"); assert sr == 48000
    b1=[1.53512485958697,-2.69169618940638,1.19839281085285]; a1=[1,-1.69065929318241,0.73248077421585]
    b2=[1,-2,1]; a2=[1,-1.99004745483398,0.99007225036621]
    z = ss.lfilter(b2, a2, ss.lfilter(b1, a1, y, axis=0), axis=0)
    B, S = int(0.4*sr), int(0.1*sr)
    ms = np.array([np.mean(z[i:i+B]**2, axis=0).sum() for i in range(0, len(z)-B+1, S)])
    L = -0.691 + 10*np.log10(ms + 1e-30)
    g = ms[L > -70]; rel = -0.691 + 10*np.log10(g.mean()) - 10
    I = -0.691 + 10*np.log10(ms[(L > -70) & (L > rel)].mean())
    tp = 20*np.log10(np.abs(ss.resample_poly(y, 4, 1, axis=0)).max())
    print(f"{f.split('/')[-1]}: I={I:.2f} LUFS  TP(4x)={tp:.2f} dBTP  samples={len(y)} dur={len(y)/sr:.4f}s")
