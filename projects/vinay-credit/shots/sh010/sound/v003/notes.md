# sh010 sound v003: one real trailer bed, no synthetic SFX

## What
- **Bed:** `source/trailer.mp4` from 61.00 to 76.00 s, one continuous take for all 15.000 s (720000 samples, 48 kHz stereo). 0.15 s raised-cosine fade-in, 0.7 s fade-out from 14.30. Never ducked or cut.
- **Focus pull:** time-varying 4-pole Butterworth low-pass with exponential steps every 10 ms, 20 kHz down to 1.8 kHz from 7.90 to 10.15, plus a +2 dB low shelf at 150 Hz that ramps in with it. It eases dry to filtered over 7.90-8.10, then **snaps fully open in 20 ms (10.150-10.170)**, ending on the lock-hit onset.
- **Sub layers:** `sfx/boom.wav` low-passed at 90 Hz twice, 0.3 s fade, gain set -14 dB under the local bed RMS.
  - Start 0.95 (0.5 s long, ends 1.45 so it clears the "ROUND ONE!" call); peak 1.05.
  - Start 10.13 (0.8 s); peak 10.23.
  - Start 12.29 (0.8 s), after the silence; peak 12.39.
- **Trailer punch:** trailer 142.78-143.10, high-pass 120 Hz, 40 ms fade-in and 120 ms fade-out, -8 dB under the local bed RMS. Its transient sits at **10.18**.
- **Banned and absent:** shimmer, riser, whoosh, glitch, swipe, reverse, tape-stop, downlifter, drones, chimes, tracker ticks. The whooshes heard at 0.60-1.00 and 9.40-10.19 are part of the bed itself.
- **"ROUND ONE!":** the film's own announcer, at 1.52-2.52 (Whisper). Kept, per the producer. It is not notched, no accent overlaps it (asserted in code) and nothing ducks it. Master vs source bed correlation over 1.45-2.70 is 1.0000.

## Measured (onset detection and RMS at 10 ms on the raw bed; matches audio/v001/beats.json)
| event | measured t (bed) | trailer s | frame |
|---|---|---|---|
| opening hit | onset 1.00, peak 1.03 | 62.00 | 25 |
| lock hit | onset 10.17-10.19, loudest RMS 10.24-10.27 (-7.9 dB) | 71.18 | 255 (10.20) |
| silence | below -30 dB RMS 11.97-12.26 (core 11.98-12.24, -34 to -40 dB) | 72.97-73.26 | 299-306 |
| drop | rise 12.28, onset 12.30, transient 12.35 | 73.30 | 307 (12.28) |
Measured on the master: lock onset 10.17-10.19, drop 12.30 / 12.35, silence 11.98-12.26 at -35.6 dB. The silence is bit-identical to the accent-free mix (no accent energy in 11.94-12.28, asserted in code).

## Master
`work/master.sh` runs these steps:
1. `work/peak_limit.py`: numpy look-ahead true-peak limiter at -5.2 dBTP (3 ms attack, 80 ms release).
2. `tools/vfx/bin/master_audio.sh ... youtube`; loudnorm second pass confirmed **linear**.
3. A static +0.28 dB trim. On this 15 s file loudnorm's internal meter reads 0.3 LU hotter than ebur128 / BS.1770, so the tool alone lands at -14.3.

- **Result:** `mix_master.wav` measures **-14.00 LUFS, -1.04 dBTP, LRA 3.4**, pcm_s24le, 48 kHz stereo, 720000 samples = 15.000 s. The no-accent version measures the same.
- **Why the limiter:** the source bed alone is -14.8 LUFS at -0.5 dBTP, so -14/-1 cannot be reached without peak control. Without the pre-limit, loudnorm falls back to dynamic AGC mode, which pumps the music.
- **Limiter gain reduction:**
  - Bed regions: up to 1.0-1.35 dB.
  - The lock (10.2-10.45): 3.1 dB, of which about 1.4 dB is caused by the punch layer.
  - The drop (12.35-12.6): 2.5 dB.
  - Accent-free version: 1.7 dB maximum.
- **Self-check:** Whisper (small, VAD) on mix_master.wav returns exactly one segment, "Round one!" at 1.52-2.52, which is the kept announcer. No other words.

## Files
- `mix_raw.wav`: unmastered mix with a -3 dB static trim, float32.
- `mix_master.wav`: the deliverable.
- `mix_noaccents_raw.wav`, `mix_master_no_accents.wav`: bed with fades only (no focus pull, no subs, no punch), for the conform A/B.
- `cues.json`: every timing, level and measurement.
- `work/build_mix.py`, `work/peak_limit.py`, `work/master.sh`, `work/lufs.py`: the build and master chain.
- `work/stem_*.wav`, `work/spectrogram_*.png`, `work/whisper_master.json`: QC material.

Rebuild with: `cd work && vfx-python build_mix.py $PWD ../../../../../sfx && bash master.sh`
