# sh010 sound v003 - the bed's own decay instead of digital silence

This addresses VFX supervisor note 6. In v002, f132-163 was digital zero, which can read as a dropout on phones. v002 is kept.
v003 is **bit-identical to v002 everywhere except src 117.30-118.70** (t 5.20-6.60). Max sample difference outside that span is 0.0.

## The change
- The dry bed fades 117.30 → 117.38 (raised cosine), as in v002.
- The gap is now the real music decaying. Bed audio from 117.10 to 117.38 (the last ~200 ms plus the 80 ms fade) is convolved with a stereo damped-noise reverb:
  - RT60 is 2.6 s at 250 Hz and below, falling to about 1.2 s at 8 kHz, so the highs die first.
  - The reverb is level-matched 2 dB under the dry and crossfaded in over 117.30-117.38.
  - The reverb input ends at 117.38. "You lose" begins at about 117.37-117.64 (formants from about 117.65), and the input gain at 117.37 is about 0.4%, so no voice feeds the tail.
- Decay (10 ms RMS, master): -22.5 dBFS at 117.30, -30.6 at 117.40, -45.5 at 118.10, **-46.0 at 118.40**, -52.6 at 118.60, minimum **-61 dBFS** at about 118.66. There is no digital zero.
- The join is a 20 ms raised-cosine crossfade over 118.68-118.70, tail out and untouched bed in. From **118.70 on, the bed is untouched**; it returns at its own -31 dB level.
- No added noise, tones or SFX. The near-silence is the music's own reverb decay.
- The tail is the same as v002: fade 13.40-14.00, then silence.

## Master
mix_master.wav is 720000 samples (15.000 s), 48 kHz stereo, 24-bit, with 0 lag against the source.

| | Loudness | True peak |
|---|---|---|
| mix_master.wav | -14.0 LUFS, LRA 3.0 LU | -1.50 dBTP, sample peak -1.57 dBFS |
| AAC 320k `-cutoff 20000` | -14.0 LUFS | -1.52 dBTP |
| AAC 192k `-aac_coder fast -cutoff 20000` | -14.0 LUFS | -1.71 dBTP |

Both AAC encodes are within -1.0.
Mastering is the same as v002: +0.10 dB static gain plus a 4x-oversampled peak limiter at -1.5 dBTP (max gain reduction 1.39 dB on 1.03% of samples).

## Gates
- **Whisper:** small + medium on the whole bed plus 7 windows covering 115.1-120.6, 16 runs in all. Result: **no words** (qc/whisper_gate.txt, qc/transcripts/). The tail is identical to v002, which passed 28/28.
- **Onsets (unchanged):** f173 HERO 6.92 (0.00 frames off; librosa peaks 6.885/6.945). f275 TITLE 10.99-11.005 (-0.25 to +0.13 frames).
- **Visual:** qc/AB_spectrogram_v002_vs_v003_src116.0-119.5.png shows a natural ring-out of the ~600 Hz tone with no edges. qc/qc_envelope_v001_v002_v003.png overlays all three versions.

## Commands
- `vfx-python scripts/bed_edit_v003.py bed_soxr_raw.wav bed_v003.wav 2.6`
  - bed_soxr_raw is source/trailer.mp4 with `aresample=48000:resampler=soxr:precision=28,atrim=112.10:127.10`.
  - The IR uses a fixed seed (173), so the output is reproducible.
- `vfx-python scripts/master.py bed_v003.wav mix_master.wav -1.5 -14.0`

## Note for the client rule
The reverb is processing of the real trailer audio, as the supervisor's note intends. It is not a separate sound element, but it is the first processing applied to the music itself; treatment section 10 says "none on the music". Flag this to the director if the client is strict.
