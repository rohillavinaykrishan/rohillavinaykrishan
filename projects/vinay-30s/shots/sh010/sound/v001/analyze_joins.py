# Join analysis: waveform +-120 ms, spectrogram +-600 ms, HF (>6 kHz) click energy per 1 ms around each splice.
# usage: vfx-python analyze_joins.py in.wav out.png [label]
import sys, numpy as np, soundfile as sf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.signal import butter, sosfilt
y, sr = sf.read(sys.argv[1]); m = y.mean(1)
J = [9.475, 14.270, 19.385]
sos = butter(4, 6000, 'hp', fs=sr, output='sos'); hp = sosfilt(sos, m)
fig, ax = plt.subplots(3, 3, figsize=(18, 10))
for i, t in enumerate(J):
    c = int(t*sr)
    w = int(0.12*sr); seg = y[c-w:c+w]; tt = (np.arange(-w, w))/sr*1000
    ax[0,i].plot(tt, seg[:,0], lw=.5); ax[0,i].plot(tt, seg[:,1], lw=.5, alpha=.6); ax[0,i].axvline(0, c='r', lw=.8)
    ax[0,i].set_title(f'join {i+1} @ {t:.3f}s waveform (ms)')
    w2 = int(0.6*sr); s2 = m[c-w2:c+w2]
    ax[1,i].specgram(s2, NFFT=1024, Fs=sr, noverlap=896, cmap='magma', vmin=-140)
    ax[1,i].axvline(0.6, c='c', lw=.8); ax[1,i].set_ylim(0, 20000); ax[1,i].set_title('spectrogram +-0.6 s')
    # HF energy, 1 ms blocks, +-60 ms
    b = int(0.001*sr); w3 = int(0.06*sr); h = hp[c-w3:c+w3]
    e = 20*np.log10(np.sqrt((h[:len(h)//b*b].reshape(-1,b)**2).mean(1))+1e-9)
    ax[2,i].plot(np.arange(len(e))-60, e); ax[2,i].axvline(0, c='r', lw=.8); ax[2,i].set_title('HF>6k RMS dB per ms')
    # stats
    pre = m[c-int(.05*sr):c]; post = m[c:c+int(.05*sr)]
    rms = lambda a: 20*np.log10(np.sqrt((a**2).mean())+1e-9)
    loc = e[55:66].max(); ctx = np.median(np.r_[e[:45], e[75:]])
    d = np.abs(np.diff(y[c-200:c+200], axis=0)).max(); dctx = np.percentile(np.abs(np.diff(y[c-4800:c+4800], axis=0)), 99.9)
    print(f'join{i+1} t={t}: rms50ms pre {rms(pre):.1f} post {rms(post):.1f} dB | HF peak@join {loc:.1f} vs median ctx {ctx:.1f} (+{loc-ctx:.1f} dB) | max|dx| join {d:.4f} vs p99.9 ctx {dctx:.4f}')
fig.suptitle(sys.argv[3] if len(sys.argv) > 3 else sys.argv[1]); fig.tight_layout(); fig.savefig(sys.argv[2], dpi=70)
