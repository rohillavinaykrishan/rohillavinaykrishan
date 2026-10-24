# sync proof: 10 ms sub-band (<120 Hz) RMS + full-band onset strength of master.wav vs f261 and the beat grid.
# usage: vfx-python sync_proof.py  -> sync_proof.png, work/sync.json
import json, numpy as np, soundfile as sf, scipy.signal as ss, librosa
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SR, FPS = 48000, 25
cues = json.load(open('../../director/v001/cues.json')); beats = cues['beats_f']
y, sr = sf.read('master.wav'); m = y.mean(1)
dry, _ = sf.read('master_nocharge.wav')
hop = 480                                                     # 10 ms
sos = ss.butter(4, 120, 'low', fs=SR, output='sos'); sub = ss.sosfiltfilt(sos, m)
def rms_db(v): 
    n = len(v)//hop; f = v[:n*hop].reshape(n, hop); return 20*np.log10(np.sqrt((f**2).mean(1))+1e-9)
sub_db = rms_db(sub); full_db = rms_db(m); t = (np.arange(len(sub_db))+0.5)*hop/SR
# biggest 0.3 s sub-band rise in the window; onset = first 10 ms hop where the jump starts (>6 dB above hole median)
d = sub_db[30:] - sub_db[:-30]; k = int(np.argmax(d))
# drop onset = 5 ms block after the sub minimum (10.30-10.44 s, after the 126.48 pickup) where the sub crosses the
# hole/plateau midpoint and the following 100 ms stays above it on average (sustained plateau, not a pickup hit)
h5 = 240; n5 = len(sub)//h5; s5 = 20*np.log10(np.sqrt((sub[:n5*h5].reshape(n5,h5)**2).mean(1))+1e-9)
i0, i1 = int(10.30*SR/h5), int(10.44*SR/h5); imin = i0 + int(np.argmin(s5[i0:i1])); hole = float(s5[imin])
plat = float(np.median(s5[int(10.6*SR/h5):int(11.4*SR/h5)])); mid = (hole + plat)/2
on = next(i for i in range(imin, imin+100) if s5[i] > mid and s5[i:i+20].mean() > mid)
on_s = on*h5/SR; on_f = on_s*FPS; pick_s = (int(10.0/0.01)+int(np.argmax(sub_db[int(10.0/0.01):int(10.40/0.01)])))*hop/SR
# full-band onset strength (librosa, 10 ms hop) and onset peaks
oenv = librosa.onset.onset_strength(y=m.astype(np.float32), sr=SR, hop_length=hop)
ot = librosa.times_like(oenv, sr=SR, hop_length=hop)
peaks = librosa.onset.onset_detect(onset_envelope=oenv, sr=SR, hop_length=hop, units='time')
sk = ot > 0.2; strongest = float(ot[sk][np.argmax(oenv[sk])])  # skip the file-start edge
near261 = float(peaks[np.argmin(np.abs(peaks - 261/FPS))])
# HF energy (>5 kHz) of master vs nocharge: shows the charge low-pass and the bypass
sos_h = ss.butter(4, 5000, 'high', fs=SR, output='sos')
hf_w = rms_db(ss.sosfilt(sos_h, m)); hf_d = rms_db(ss.sosfilt(sos_h, dry.mean(1)))
res = dict(sub_jump_db_0p3s=round(float(d[k]),1), sub_jump_start_s=round(k*hop/SR,3), sub_hole_min_db=round(hole,1), sub_hole_min_s=round(imin*h5/SR,3), sub_plateau_db=round(plat,1), pickup_sub_peak_s=round(pick_s,3),
           sub_onset_s=round(on_s,3), sub_onset_frame=round(on_f,2), sub_onset_err_frames=round(on_f-261,2),
           strongest_fullband_onset_s=round(strongest,3), strongest_onset_frame=round(strongest*FPS,2),
           onset_nearest_f261_s=round(near261,3), onset_nearest_f261_err_frames=round(near261*FPS-261,2),
           max_diff_after_f261=float(np.abs(y[501120:]-dry[501120:]*(y[600000:700000].std()/dry[600000:700000].std())).max()))
json.dump(res, open('work/sync.json','w'), indent=1); print(json.dumps(res))
fig, ax = plt.subplots(3, 1, figsize=(16, 11), gridspec_kw=dict(height_ratios=[1.2, 1.4, 1]))
F = t*FPS
for a in ax:
    for b in beats: a.axvline(b, color='0.8', lw=0.8, zorder=0)
a = ax[0]; a.plot(F, full_db, color='0.4', lw=0.8, label='full-band RMS (10 ms)'); a.plot(F, sub_db, color='C3', lw=1.2, label='sub <120 Hz RMS (10 ms)')
a.axvline(261, color='k', lw=1.5, label='f261 DROP'); a.axvspan(219, 261, color='C0', alpha=0.08, label='charge f219-260')
a.axvspan(0,3,color='C2',alpha=0.3,label='head fade f0-3'); a.axvspan(425,450,color='C2',alpha=0.15,label='tail fade f425-450')
a.set_xlim(0,450); a.set_ylabel('dB'); a.set_title('sh010 sound v001 master.wav: whole 18.0 s (grey lines = beat frames from cues.json)'); a.legend(loc='lower left', fontsize=8, ncol=4)
z = (F>=200)&(F<=300)
a = ax[1]; a.plot(F[z], sub_db[z], color='C3', lw=1.5, label='sub <120 Hz RMS'); a.plot(F[z], full_db[z], color='0.4', lw=1, label='full-band RMS')
a.plot(F[z], hf_d[z], color='C1', lw=0.9, ls='--', label='>5 kHz, no-charge master'); a.plot(F[z], hf_w[z], color='C0', lw=1.2, label='>5 kHz, master (charge LPF)')
a.axvline(261, color='k', lw=2); a.axvline(on_f, color='C3', ls=':', lw=2, label=f'drop sub onset f{on_f:.2f} ({on_f-261:+.2f} f)')
a.axvspan(254, 259.5, color='C1', alpha=0.07, label='126.48 pickup (has its own sub)')
for p in peaks:
    if 200 <= p*FPS <= 300: a.axvline(p*FPS, color='C4', lw=0.8, ymax=0.08)
a.axvspan(260,262,color='y',alpha=0.25,label='f261 ±1 frame')
a.set_xlim(200,300); a.set_xticks(range(200,301,5)); a.set_ylabel('dB'); a.legend(loc='lower left', fontsize=8, ncol=3)
a.set_title(f'zoom f200-300: sub jump {d[k]:+.1f} dB in 0.3 s; LPF bypassed at sample 501120 = 10.440 s = f261 (purple ticks = onset peaks)')
a = ax[2]; zo = (ot*FPS>=200)&(ot*FPS<=300); a.plot(ot[zo]*FPS, oenv[zo], color='C4'); a.axvline(261, color='k', lw=2)
a.axvline(strongest*FPS, color='C3', ls=':', label=f'strongest full-band onset (t>0.2 s) at f{strongest*FPS:.2f}'); a.set_xlim(200,300); a.set_xticks(range(200,301,5)); a.set_xlabel('frame (25 fps)'); a.set_ylabel('onset strength'); a.legend(fontsize=8)
plt.tight_layout(); plt.savefig('sync_proof.png', dpi=90)
