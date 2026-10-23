# Click detector: LPC(order 32) residual peak within +-4 ms of each splice vs the 99.9th pct of the residual over +-300 ms.
# A ratio < 1 means the splice is no sharper than the music around it. usage: vfx-python clickscore.py a.wav [b.wav ...]
import sys, numpy as np, soundfile as sf, librosa
from scipy.signal import lfilter
J = [9.475, 14.270, 19.385]
for f in sys.argv[1:]:
    y, sr = sf.read(f); m = y.mean(1); r = []
    for t in J:
        c = int(t*sr); w = int(.3*sr); x = m[c-w:c+w].astype(np.float64)
        a = librosa.lpc(x, order=32); e = np.abs(lfilter(a, [1], x))
        k = int(.004*sr); loc = e[w-k:w+k].max(); ctx = np.percentile(np.r_[e[:w-k*5], e[w+k*5:]], 99.9)
        r.append(round(loc/ctx, 2))
    print(f.split('/')[-1], 'join ratios', r)
