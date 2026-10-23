# Sync proof on the final master: waveform + spectrogram +-6 frames around f365 (HIT) and f686 (TITLE), 25 fps frame grid,
# measured transient (max 5 ms RMS rise of a 1 ms envelope), H0 plate frames 0/1 (= f365/f366) as picture reference.
import numpy as np, soundfile as sf, matplotlib, json; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.image as mpimg
y, sr = sf.read('master.wav'); m = y.mean(1); FPS = 25
def onset(t0, t1):
    x = m[int(t0*sr):int(t1*sr)]; b = int(.001*sr); e = 20*np.log10(np.sqrt((x[:len(x)//b*b].reshape(-1, b)**2).mean(1))+1e-9)
    d = e[5:]-e[:-5]; j = int(np.argmax(d)); return t0 + j*.001, t0 + (j+5)*.001   # rise start, rise end
fig = plt.figure(figsize=(18, 11)); gs = fig.add_gridspec(3, 3, width_ratios=[3, 3, 2])
res = {}
for col, (name, f, t0, t1) in enumerate([('HIT f365', 365, 14.45, 14.75), ('TITLE f686', 686, 27.25, 27.6)]):
    a, b = onset(t0, t1); res[name] = (a, b)
    w0, w1 = (f-6)/FPS, (f+6)/FPS; i0, i1 = int(w0*sr), int(w1*sr); tt = np.arange(i0, i1)/sr
    ax = fig.add_subplot(gs[0, col]); ax.plot(tt, y[i0:i1, 0], lw=.4); ax.plot(tt, y[i0:i1, 1], lw=.4, alpha=.6)
    ax.set_ylim(-1, 1); ax.axhline(10**(-2/20), c='k', lw=.4, ls=':'); ax.axhline(-10**(-2/20), c='k', lw=.4, ls=':')
    ax2 = fig.add_subplot(gs[1, col]); ax2.specgram(m[i0:i1], NFFT=512, Fs=sr, noverlap=448, cmap='magma', vmin=-130, xextent=(w0, w1)); ax2.set_ylim(0, 16000)
    for A in (ax, ax2):
        for k in range(f-6, f+7):
            A.axvline(k/FPS, c='grey', lw=.4, alpha=.6)
        A.axvspan(f/FPS, (f+1)/FPS, color='lime', alpha=.18); A.axvline(a, c='r', lw=1.2); A.set_xlim(w0, w1)
    ax.set_xticks([k/FPS for k in range(f-6, f+7, 2)]); ax.set_xticklabels([f'f{k}' for k in range(f-6, f+7, 2)])
    off = (a - f/FPS)*FPS
    ax.set_title(f'{name}: frame {f} = {f/FPS:.3f}-{(f+1)/FPS:.3f} s (green)\ntransient rise {a:.3f}-{b:.3f} s (red) = {off:+.2f} f  ->  {"PASS" if abs(off) <= 1 else "FAIL"} (+-1 f)', fontsize=10)
    ax2.set_title('spectrogram, 25 fps frame grid', fontsize=9)
for r, k in enumerate([1, 2]):
    ax = fig.add_subplot(gs[r, 2]); ax.imshow(mpimg.imread(f'work/h0_{k}.png')); ax.axis('off'); ax.set_title(f'edit H0 plate frame {k-1} = master f{364+k}' + (' (glove contact)' if k == 1 else ''), fontsize=9)
ax = fig.add_subplot(gs[2, :]); t = np.arange(len(m))/sr; b = int(.01*sr); pk = np.abs(y).max(1)[:len(m)//b*b].reshape(-1, b).max(1)
ax.plot(np.arange(len(pk))*.01, 20*np.log10(pk+1e-9), lw=.5); ax.set_ylim(-60, 0); ax.set_xlim(0, 30)
for s in [9.475, 14.27, 19.385]: ax.axvline(s, c='b', lw=.6, ls='--')
for n, (a, _) in res.items(): ax.axvline(a, c='r', lw=1)
ax.axhline(-2, c='k', lw=.4, ls=':'); ax.set_title('master.wav full 30.000 s, 10 ms peak dBFS: blue = splices (9.475 / 14.270 / 19.385), red = HIT / TITLE transients; dotted -2 dBFS', fontsize=10)
fig.suptitle('vinay-30s sh010 sound v001 sync proof (master.wav, 48 kHz, -14.0 LUFS, -2.0 dBTP)', fontsize=12); fig.tight_layout(); fig.savefig('sync_proof.png', dpi=80)
json.dump({k: {'rise_start_s': round(v[0], 4), 'rise_end_s': round(v[1], 4)} for k, v in res.items()}, open('work/sync_onsets.json', 'w'), indent=1); print(res)
