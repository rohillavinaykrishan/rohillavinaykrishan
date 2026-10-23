# sh010 sound v001 (Sound, treatment row #13)

**Deliverable:** `master.wav`: 48 kHz, stereo, PCM 24-bit, 864000 samples = 18.000 s exactly.
**A/B:** `master_nocharge.wav` is identical except for the charge filter (same cut and fades, also at -14 LUFS).
No SFX or synthetic layers: the client's track only (`source/client_music.mp3` 116.30-134.30).

## Chain (`process.py` -> `master.py`)
1. Decode the MP3 to 48 kHz float32 (soxr) with `ffmpeg -i source/client_music.mp3 -af aresample=48000:resampler=soxr:precision=28 -c:a pcm_f32le work/full48.wav`.
   Then cut samples 5582400 to 6446400 (116.300 to 134.300 s). This cross-correlates to the director's bed at offset 0 (r = 0.998),
   so it uses the same timebase as the cues.json analysis. The source has MP3 overs up to +1.9 dBFS. The director's 16-bit bed clips them at 1.0;
   this float path keeps them, and the master gain brings them back under 0 dBFS cleanly. Nothing is clipped at any stage.
2. Head fade: f0-3 (120 ms), sine curve.
3. Charge: a TPT state-variable low-pass (12 dB/oct, Butterworth Q, no resonance), swept exponentially from 20 kHz to 2.5 kHz over f219-f258
   and held to f260. It has a gain dip from 0 to -1.5 dB on the same ramp. **Bypass:** a 1 ms (48-sample) crossfade that *ends* on sample 501120 = 10.440 s = f261.
   From f261 on, the output is bit-identical to the no-charge version (asserted in the script; measured max diff 1.2e-7 after level match).
   The step at the bypass is within normal sample-to-sample deltas (0.228 vs a 99.9th percentile of 0.225), so there is no click.
4. Tail fade: f425 to the end (17.0-18.0 s), equal-power cosine. The last sample is 0.
5. Master: **static gain only** (-6.89 dB; no limiter, compressor or loudnorm dynamics). The true peak is far under the ceiling, so nothing else is needed.
   `tools/vfx/bin/master_audio.sh` was not used because its ceiling is -1 dBTP and the brief asks for <= -1.5. It also falls back to loudnorm dynamic mode on short files.

## Measurements (ffmpeg loudnorm / ebur128, true peak 4x)
| file | I (LUFS) | TP (dBTP) | LRA |
|---|---|---|---|
| master.wav | -14.01 | -4.31 | 2.7 |
| master.wav -> AAC 320k `-cutoff 20000` | -14.08 | -4.60 | |
| master_nocharge.wav | -14.00 | -4.37 | 2.7 |
| master_nocharge.wav -> AAC 320k | -14.07 | -4.71 | |
The sample peak of master.wav is -4.94 dBFS. The pre-gain mix measured -7.11 LUFS / +2.58 dBTP.

## Sync (`sync_proof.py` -> `sync_proof.png`, numbers in `work/sync.json`)
- Drop sub-band (<120 Hz, 5 ms) onset: **10.430 s = f260.75 (-0.25 f)**. The sub hole minimum is -47.1 dB at 10.41 s; the plateau is -15.1 dB.
  The sub rises +34.4 dB within 0.3 s. The onset strength peak nearest f261 is at 10.45 s = f261.25 (+0.25 f). Both are within ±1 f.
- Caveat for QC: the 126.48 pickup (f254-259) has its own sub-band hit at 10.25 s (f256). A naive "first sub rise after the hole" detector
  fires there (-5 f). The sustained drop plateau starts at f261. The proof marks the pickup span.
- Strongest full-band spectral-flux onset in the 18 s is fill_3 at f231.25, not the drop. The drop is the biggest *sub/RMS contrast* event,
  which matches the treatment ("a contrast event, not a loud one").

## Whisper gate (VAD off; director's `whisper_vadoff.py`, faster-whisper small int8) -> `whisper_master_vadoff.json`
One segment: " Music" at 3.10-4.50 s (no_speech_prob 0.52, avg_logprob -1.49). This is Whisper's non-speech tag for instrumentals, not a lyric.
No real words. (The director's run on the raw bed gave the "THANKS FOR WATCHING!" hallucination at 5.46-7.40 s.)

## Taste / open item
The charge takes >5 kHz content down by about 15-20 dB by f245 (see the zoom panel). It reads as a clear "muffle then open" and pairs with the colour unlock.
If the director finds it too effect-like, halving it means changing the end cutoff in `process.py` from 2500 to about 5000 Hz. A/B against `master_nocharge.wav`.

Regenerate: decode step 1, then `vfx-python process.py && vfx-python master.py work/mix_charge.wav master.wav && vfx-python master.py work/mix_dry.wav master_nocharge.wav && vfx-python sync_proof.py`.
