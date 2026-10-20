"""sh010 sound v003: one real trailer bed + focus-pull + 3 sub layers + trailer punch. No synthetic SFX."""
import json, sys, numpy as np, soundfile as sf, scipy.signal as ss
W = sys.argv[1]; SFX = sys.argv[2]
SR = 48000; N = 15 * SR                      # exactly 720000 samples
T = json.load(open(f"{W}/../cues.json"))
bed, sr = sf.read(f"{W}/bed_long.wav", dtype="float64"); assert sr == SR
bed = bed[:N].copy()
t = np.arange(N) / SR

# ---- fades (bed): 0.15 s in, 0.7 s out from 14.3 (raised-cosine)
g = np.ones(N)
fi = t < 0.15; g[fi] = 0.5 - 0.5 * np.cos(np.pi * t[fi] / 0.15)
fo = t >= 14.3; g[fo] = 0.5 + 0.5 * np.cos(np.pi * np.clip((t[fo] - 14.3) / 0.7, 0, 1))

# ---- focus pull: time-varying 4-pole Butterworth low-pass + low-shelf, 10 ms coefficient steps
fp = T["focus_pull"]; a0, a1, snap0, snap1 = fp["start"], fp["full_at"], fp["snap_start"], fp["snap_end"]
def biquad(kind, f, q=0.7071, gdb=0.0):
    w = 2 * np.pi * f / SR; cw, sw = np.cos(w), np.sin(w); al = sw / (2 * q); A = 10 ** (gdb / 40)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    else:  # low shelf (RBJ, S=1)
        al = sw / 2 * np.sqrt(2); sA = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + sA), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sA)]
        a = [(A + 1) + (A - 1) * cw + sA, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sA]
    return np.r_[np.array(b) / a[0], np.array(a) / a[0]]
i0 = int((a0 - 0.05) * SR); i1 = int((snap1 + 0.05) * SR); H = 480
seg = bed[i0:i1]; out = np.zeros_like(seg); zi = np.zeros((3, 2, 2))
for k in range(0, len(seg), H):
    tc = (i0 + k) / SR
    x = np.clip((tc - a0) / (a1 - a0), 0, 1)
    fc = 20000 * (1800 / 20000) ** x                     # exponential sweep 20k -> 1.8k
    sos = np.stack([biquad("lp", fc, 0.5412), biquad("lp", fc, 1.3066), biquad("ls", 150, gdb=2.0 * x)])
    for ch in range(2):
        out[k:k + H, ch], zi[:, :, ch] = ss.sosfilt(sos, seg[k:k + H, ch], zi=zi[:, :, ch])
wet = np.zeros(N); 
m = (t >= a0) & (t < a0 + 0.2); wet[m] = (t[m] - a0) / 0.2           # ease dry->filtered over 0.2 s
wet[(t >= a0 + 0.2) & (t < snap0)] = 1
m = (t >= snap0) & (t < snap1); wet[m] = 1 - (t[m] - snap0) / (snap1 - snap0)   # snap open (20 ms)
filt = bed.copy(); filt[i0:i1] = out
bed_fx = (bed * (1 - wet)[:, None] + filt * wet[:, None]) * g[:, None]
bed_plain = bed * g[:, None]

def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-20)
def lr(x, f, kind, order=2, passes=1):
    b, a = ss.butter(order, f / (SR / 2), kind)
    for _ in range(passes): x = ss.lfilter(b, a, x, axis=0)
    return x
acc = np.zeros((N, 2)); report = []
# ---- deep sub layers: boom.wav, lowpass 90 Hz x2, <=0.8 s, 0.3 s fade, gain -14 dB under local bed RMS
boom, _ = sf.read(f"{SFX}/{T['sub']['source']}", dtype="float64")
sub = lr(boom, 90, "low", 2, 2)[: int(0.8 * SR)]
pk_off = np.argmax(np.abs(sub).sum(1)) / SR
for c in T["sub"]["hits"]:
    st = int(round((c["t"] - c["lead"]) * SR)); L = min(int(c.get("len", 0.8) * SR), N - st)
    sl = sub[:L].copy(); nf2 = min(int(0.3 * SR), L); sl[-nf2:] *= np.linspace(1, 0, nf2)[:, None]
    win = bed_fx[st:st + L]; gain = 10 ** (T["sub"]["gain_db_under_bed"] / 20) * rms(win) / rms(sl)
    acc[st:st + L] += sl * gain
    report.append(dict(layer="sub", start=st / SR, end=(st + L) / SR, peak_at=st / SR + pk_off, gain_lin=gain))
# ---- trailer punch: 142.78-143.10, highpass 120, 40 ms in / 120 ms out, -8 dB under local bed RMS
p, _ = sf.read(f"{W}/punch_src.wav", dtype="float64")
p = lr(p, 120, "high", 2, 1)
e = np.ones(len(p)); a_ = int(0.04 * SR); r_ = int(0.12 * SR); e[:a_] = np.linspace(0, 1, a_); e[-r_:] = np.linspace(1, 0, r_); p *= e[:, None]
env = np.abs(p).sum(1); tr = np.argmax(env > 0.5 * env.max()) / SR       # transient = first sample above half peak
pc = T["punch"]; st = int(round((pc["t"] - tr) * SR)); L = len(p)
gain = 10 ** (pc["gain_db_under_bed"] / 20) * rms(bed_fx[st:st + L]) / rms(p)
acc[st:st + L] += p * gain
report.append(dict(layer="punch", start=st / SR, end=(st + L) / SR, transient_at=st / SR + tr, gain_lin=gain))

# ---- silence guard: nothing but the bed inside the silence
a_, b_ = T["announcer_keep_clear"]
assert np.abs(acc[int(a_ * SR):int(b_ * SR)]).max() == 0, "accent overlaps the ROUND ONE call"
s0, s1 = T["silence_keep_clean"]
assert np.abs(acc[int(s0 * SR):int(s1 * SR)]).max() == 0, "accent leaks into the silence"
mix = bed_fx + acc
trim = T["mix_trim_db"]; tg = 10 ** (trim / 20)
sf.write(f"{W}/../mix_raw.wav", mix * tg, SR, subtype="FLOAT")
sf.write(f"{W}/../mix_noaccents_raw.wav", bed_plain * tg, SR, subtype="FLOAT")
sf.write(f"{W}/stem_accents.wav", acc * tg, SR, subtype="FLOAT")
sf.write(f"{W}/stem_bed_fx.wav", bed_fx * tg, SR, subtype="FLOAT")
for r in report: r["gain_db"] = 20 * np.log10(r.pop("gain_lin"))
print(json.dumps(report, indent=1)); print("mix peak dBFS", 20 * np.log10(np.abs(mix * tg).max()), "samples", len(mix))
