"""Transparent look-ahead true-peak limiter (4x oversampled detection). Usage: in.wav out.wav ceiling_dBTP"""
import sys, numpy as np, soundfile as sf, scipy.signal as ss
from scipy.ndimage import minimum_filter1d
x, sr = sf.read(sys.argv[1], dtype="float64"); ceil = 10 ** (float(sys.argv[3]) / 20)
up = ss.resample_poly(x, 4, 1, axis=0); pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(x)]
need = np.minimum(1.0, ceil / np.maximum(pk, 1e-12))
la = int(0.003 * sr)                                   # 3 ms look-ahead / attack
g = minimum_filter1d(need, size=2 * la + 1, mode="nearest")
# release: one-pole 80 ms towards 1, never above the required gain
a = np.exp(-1 / (0.080 * sr)); out = np.empty_like(g); s = 1.0
for i, v in enumerate(g):
    s = v if v < s else a * s + (1 - a) * v
    out[i] = s
k = np.hanning(2 * la + 1); k /= k.sum()                # smooth the attack edge
gs = np.minimum(np.convolve(np.pad(out, la, mode="edge"), k, mode="valid"), out)
y = x * gs[:, None]; sf.write(sys.argv[2], y, sr, subtype="FLOAT")
gr = 20 * np.log10(gs); h = sr // 100
blk = np.array([gr[i:i + h].min() for i in range(0, len(gr), h)])
print(f"[{sys.argv[1].split('/')[-1]}] max GR {gr.min():.2f} dB; 10ms blocks with >0.5 dB GR: {(blk < -0.5).sum()}/{len(blk)}; >1 dB at t=",
      [round(i * 0.01, 2) for i in np.where(blk < -1)[0]][::3])
for a_,b_ in [(4.8,5.0),(6.1,6.3),(6.9,7.9),(10.1,10.6),(12.28,12.7),(13.4,13.6),(14.0,14.2)]:
    print(f"   GR {a_}-{b_}: max {gr[int(a_*sr):int(b_*sr)].min():.2f} dB")
