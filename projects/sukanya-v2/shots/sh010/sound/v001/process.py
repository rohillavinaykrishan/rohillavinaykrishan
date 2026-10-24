# sh010 sound v001: cut 116.30-134.30 from source, head fade, "charge" low-pass f219-260 + bypass at f261, tail fade.
# usage: vfx-python process.py  (run from this folder; writes work/mix_charge.wav and work/mix_dry.wav, float32 48k)
import numpy as np, soundfile as sf, json
SR, FPS = 48000, 25
SRC_IN, DUR = 116.30, 18.0
f2s = lambda f: int(round(f * SR / FPS))            # frame -> sample (f261 -> 501120 = 10.440 s)
full, sr = sf.read('work/full48.wav', dtype='float64'); assert sr == SR
s0 = int(round(SRC_IN * SR)); N = int(round(DUR * SR))
x = full[s0:s0 + N].copy(); assert x.shape == (N, 2)

def head_tail(y):
    y = y.copy()
    h = f2s(3)                                           # 3-frame (120 ms) fade-in, sine curve
    y[:h] *= np.sin(0.5 * np.pi * (np.arange(h) / h))[:, None]
    t0 = f2s(425); n = N - t0                            # f425 -> end (1.0 s), equal-power cosine, 0 at last sample
    y[t0:] *= np.cos(0.5 * np.pi * (np.arange(1, n + 1) / n))[:, None]
    return y

def charge(y):
    """TPT state-variable low-pass (12 dB/oct, Q=0.7071) swept 20 kHz -> 2.5 kHz exponentially f219 -> f258,
    held to f261; gain dip 0 -> -1.5 dB over the same ramp. Dry is restored with a 1 ms crossfade that ENDS
    on sample f2s(261), so from f261 on the output is the untouched source."""
    a, b, c = f2s(219), f2s(258), f2s(261)
    xf = 48                                               # 1 ms crossfade, samples [c-48, c)
    seg = y[a:c]; n = len(seg); i = np.arange(n)
    ramp = np.clip(i / (b - a), 0, 1)
    fc = 20000.0 * (2500.0 / 20000.0) ** ramp
    gdb = -1.5 * ramp
    g = np.tan(np.pi * fc / SR); k = np.sqrt(2.0)
    a1 = 1 / (1 + g * (g + k)); a2 = g * a1; a3 = g * a2
    out = np.empty_like(seg)
    for ch in range(2):
        ic1 = ic2 = 0.0; v = seg[:, ch]; o = out[:, ch]
        for j in range(n):
            v3 = v[j] - ic2
            v1 = a1[j] * ic1 + a2[j] * v3
            v2 = ic2 + a2[j] * ic1 + a3[j] * v3
            ic1 = 2 * v1 - ic1; ic2 = 2 * v2 - ic2
            o[j] = v2
    out *= (10 ** (gdb / 20))[:, None]
    w = np.ones(n); w[n - xf:] = np.cos(0.5 * np.pi * (np.arange(1, xf + 1) / xf))  # wet weight -> 0 at c
    yy = y.copy()
    yy[a:c] = out * w[:, None] + seg * (1 - w)[:, None]
    return yy, dict(start_sample=a, sweep_end_sample=b, bypass_sample=c, bypass_s=c / SR)

dry = head_tail(x)
wet, info = charge(x); wet = head_tail(wet)
assert np.array_equal(wet[f2s(261):], dry[f2s(261):]), "post-f261 must equal dry"
sf.write('work/mix_charge.wav', wet.astype(np.float32), SR, subtype='FLOAT')
sf.write('work/mix_dry.wav', dry.astype(np.float32), SR, subtype='FLOAT')
print(json.dumps(dict(src_sample_in=s0, N=N, src_peak=float(np.abs(x).max()), **info)))
