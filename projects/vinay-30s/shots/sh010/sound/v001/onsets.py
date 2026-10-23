# Onset (transient) finder near the sync events: 1 ms HF envelope, max rise. usage: vfx-python onsets.py a.wav [...]
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
for f in sys.argv[1:]:
    y, sr = sf.read(f); m = y.mean(1); res = []
    for name, t0, t1 in [('HIT f365', 14.45, 14.75), ('TITLE f686', 27.25, 27.6)]:
        x = m[int(t0*sr):int(t1*sr)]; b = int(.001*sr)
        e = 20*np.log10(np.sqrt((x[:len(x)//b*b].reshape(-1, b)**2).mean(1))+1e-9)
        d = e[5:] - e[:-5]; i = int(np.argmax(d)) + 5; t = t0 + i*.001
        res.append(f'{name}: onset {t:.3f}s = f{t*25:.2f} (rise {d[i-5]:.1f} dB/5ms)')
    print(f.split('/')[-1], ' | '.join(res))
