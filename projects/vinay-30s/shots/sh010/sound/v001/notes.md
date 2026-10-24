# sh010 sound v001 (Sound, team row 7)

**Deliverable:** `master.wav`: 30.000 s exactly (1,440,000 samples), 48 kHz, stereo, PCM 24-bit. Music only, **no SFX** (treatment section 9). Because there are no effects, this file is also the "no-effects" version.

## What was done
1. **Join check on the director's bed** (`analyze_joins.py` → `work/joins_bed.png`, `work/zoom.png`): waveform ±120 ms, spectrogram ±0.6 s, HF (>6 kHz) energy per 1 ms, and an LPC-residual click score (`clickscore.py`, residual peak at the splice / 99.9th percentile of the residual in the surrounding ±300 ms; < 1 = no sharper than the music around it).
   - J1 9.475 (S1→S2): bed 0.66. The rise just before the splice is S1's own crescendo in the source (src 73.25-73.35), not a flam.
   - J2 14.270 (S2→silence): bed 0.07. A clean, deliberate hard stop into the real -43 dBFS silence. No click.
   - J3 19.385 (S3→S4): bed 0.20. Level-continuous, no click.
2. **Polish** (`polish_bed.py`): the bed is rebuilt from `director/v001/audio/trailer_48k.wav` using the same `bed_segments.json` master splice points.
   - **10 ms equal-power (sin/cos) crossfades centred on each beat-locked splice** (the director used 6 ms starting at the splice). Final click scores on the master: J1 0.26, J2 0.02, J3 0.04 (`work/joins_mix.png`). There is no broadband line at any splice.
   - **S3 taken 10 ms earlier in the source** (src 104.870-109.985, within the ±10 ms splice tuning the plan allows). The S3 in-point is still inside the source silence (-42 dB). Reason: the hit transient in the director's bed starts at **14.5717 s** (sample-accurate), not 14.594, which is 0.71 f before f365 and 22 ms outside the plan's ±20 ms. Now it starts at **14.5817 s** (12 ms before 14.594, -0.46 f). The J2 and J3 master points and S4 are unchanged, so the title hit has not moved.
   - **Head:** 5 ms sine fade-in. The source is already at -13 dB at the in-point, so the cold-open attack is kept with no step.
   - **Tail:** 0.6 s cosine fade reaching zero at master 29.985 = **src 156.525**, followed by 15 ms of digital silence. Nothing past 156.525 is used (the spoken line is at 156.69).
3. **Master** (`master.sh mix.wav master.wav 0.45 -2.0`): +0.45 dB linear gain, then `alimiter` (limit -2 dBFS, attack 2 ms, release 60 ms, latency compensated) at **4x oversampling (192 kHz, soxr)**, then 48 kHz 24-bit. `master_audio.sh youtube` gave -13.9 LUFS / -1.0 dBTP, which fails ≤ -1.5, so it was not used.
   - Limiter gain reduction: max 2.2 dB on isolated peaks, median 0 dB, 49 of 2951 10 ms blocks above 1 dB. The master is sample-aligned to the mix (cross-correlation lag 0).
   - No clipped samples. The song is never ducked: there is no processing other than gain and the limiter.

## Measurements (final master.wav)
| | Integrated | True peak | LRA |
|---|---|---|---|
| master.wav | **-14.02 LUFS** | **-2.00 dBTP** | 2.3 LU |
| AAC 320k `-cutoff 20000` (`work/master_aac320.m4a`) | -14.06 LUFS | **-1.93 dBTP** (≤ -1.0 pass) | |

## Sync proof (`sync_proof.png`, 25 fps frame grid; the H0 plate frames 0/1 are shown as picture reference)
- **HIT f365** (14.600 s): transient rise 14.578-14.583 s, first sample above the silence 14.5817 s = **-0.46 to -0.55 f → PASS (±1 f)**. The audio leads picture by about 18 ms, which is below the audio-lead detection threshold.
- **TITLE f686** (27.440 s): transient rise 27.437-27.442 s = **-0.08 f → PASS**.

## Whisper re-check, VAD OFF, on master.wav
- `whisper_vadoff.py` (small, no_speech 0.6): **0 segments** (`whisper_master_vadoff.json`).
- `whisper_vadoff_strict.py small`: 19.18-20.64 "Come on, bitches, that's a bitch." (p_nospeech 0.68). This is a mishearing of the allowed "my business" chant, in the same place as the director's run (`whisper_master_strict_small.json`).
- `whisper_vadoff_strict.py medium` (`whisper_master_strict_medium.json`):
  - 12.7-18.2 "I'm a street fighter" ×2. The sung hook is allowed; the repeat over the hit is the known hallucination.
  - 19.0-21.0 "My business as a fighter" (allowed chant).
  - Isolated digits "2 / 1 / 2 3 1 2 2 3" between 21.0 and 30.0 (p_nospeech 0.74).
- **Phrases new compared with the director's runs:**
  - The counting ("one, two, one, two, three"). It also appears on the **raw trailer** clip src 147.5-152.5 and on the director's bed clip 21-26 s (`work/whisper_clips/`), so it comes from the source music (chant/beat) and was not introduced by this polish. It is rhythmic and over the chant, so it is most likely a hallucination or chant count rather than dialogue.
  - In an earlier medium pass on the first master (before the 10 ms S3 shift), there was a one-off "What?" at 23.36-23.64 (src ≈149.90) and "I'll see you guys in the next video" at 27.9-30.0 (word p 0.04-0.12, an outro hallucination). Neither appears on the final master. The 23.36 window has no formant/harmonic voice stack (`work/spec_what_zoom.png`: broadband texture plus a falling pitched sweep).
  - **Verdict: nothing spoken detected.** Director: if you want certainty, audition src 149.6-150.2 and 147.5-152.5 (the counting) by ear.

## Re-run
```
vfx-python polish_bed.py mix.wav 10 10 10 5 0.6 0,0,-10,0
./master.sh mix.wav master.wav 0.45 -2.0
vfx-python sync_proof.py        # needs work/h0_1.png, work/h0_2.png (first 2 frames of edit/v001/plates/H0.mp4)
```
`mix.wav` is the polished, un-mastered bed (for reference).
