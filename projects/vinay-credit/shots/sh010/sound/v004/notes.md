# sh010 sound v004: re-master of v003 at a -1.5 dBTP ceiling (team-lead QC: AAC encodes exceeded -1 dBTP)

- **Same mix.** `mix_raw.wav` and `mix_noaccents_raw.wav` are byte-identical copies of v003. `cues.json` is identical. Accents, timing, the focus pull and "ROUND ONE!" are untouched; only the master changed. v003 is kept.
- **Chain** (`work/master.sh`, CEIL=-5.85):
  1. `work/peak_limit.py`: look-ahead true-peak limiter at -5.85 dBTP.
  2. `tools/vfx/bin/master_audio.sh youtube`; loudnorm second pass confirmed linear.
  3. A static +0.31 dB trim to -14.00 LUFS BS.1770.
- **mix_master.wav:** -14.00 LUFS, **-1.51 dBTP**, LRA 3.5, pcm_s24le, 48 kHz stereo, 720000 samples = 15.000 s. `mix_master_no_accents.wav` measures -14.00 LUFS, -1.52 dBTP.
- **Cost:** the limiter takes 0.65 dB more than v003. The maximum is now 3.7 dB on the lock hit (10.2-10.45) and 3.15 dB on the drop. Elsewhere it is about 1-2 dB.

## AAC verification (ffmpeg native `aac`; decoded, then measured with ebur128 and BS.1770 at 4x true peak)
| encode | LUFS | dBTP | result |
|---|---|---|---|
| 320k (`-c:a aac -b:a 320k`) | -14.04 | -1.43 | pass |
| 192k with `-cutoff 20000` | -14.13 | -1.36 | pass |
| 192k with default settings | -14.10 | **-0.73** | FAIL |

- **Why the default 192k fails:** ffmpeg's native AAC encoder creates a +2.5 dB overshoot at t=6.003, where the master is only -2.6 dBTP. This is an encoder artifact, and it does not scale with the master. A -2.0 dBTP master gave -0.07 dBTP at default 192k.
- **For share encodes, use** `-c:a aac -b:a 192k -cutoff 20000` (or `-aac_coder fast`, -1.36 dBTP), or use 320k. Re-measure the final muxed file.
- **Test files:** `work/test_aac320k.m4a`, `work/test_aac192k.m4a` (`-cutoff 20000`) and `work/test_aac192k_default.m4a` (the failing case, kept for reference).
