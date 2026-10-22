# sh010 sound v002 - real trailer bed, silence-extension edit, no SFX

Director decision: review/director_v4_quality_notes.md, "sound blocker". v001 is kept unchanged. The demucs plan was dropped; demucs never ran.

## Result
`mix_master.wav`: 720000 samples (15.000 s), 48 kHz stereo, 24-bit. It is sample-aligned with the raw bed (lag 0).

| | Loudness | True peak |
|---|---|---|
| mix_master.wav | -14.0 LUFS, LRA 3.0 LU | -1.50 dBTP (4x), sample peak -1.57 dBFS |
| AAC 320k `-cutoff 20000` | -14.0 LUFS | -1.40 dBTP |
| AAC 192k `-aac_coder fast -cutoff 20000` | -14.0 LUFS | -1.69 dBTP |

Both AAC encodes are within the -1.0 limit.

The bed is source/trailer.mp4 112.10-127.10. The only changes are fades and silence; nothing is added and nothing is synthetic.

## Edits
All times are bed time t; src = t + 112.10.
- **Fade-in:** 0-0.12 s (3 frames).
- **"You lose" removed:**
  - The bed fades out 117.30 → 117.38 (t 5.20-5.28, raised cosine) and is digital silence until 118.68 (t 6.58).
  - It then comes back with a 20 ms raised-cosine de-click ending exactly at **118.70** (t 6.60). Without it, the sound would step from zero straight into the -31 dB bed.
  - **From 118.70 on, the gain is exactly 1**, so the f173 re-entry is untouched.
  - The held breath runs f130-165 (fully silent f132-164).
- **Tail:** a linear fade 13.40 → 14.00 (src 125.50-126.10), then silence to 15.00. "I'm a street fighter" starts at 126.16, so none of it is heard. The poster hold sits over silence from 14.00.

## Gates
- **Whisper:** small + medium, 14 windows each (whole bed, plus 3-3.5 s windows at many offsets, 6 of them covering 116-119 and 2 the tail). Result: **no words in any of the 28 runs** (qc/whisper_gate.txt).
- **Onsets:**
  - **f173 HERO:** 6.92 (0.00 frames off). Flux and RMS rise agree, the pre-attack is at 6.88, and it is identical to v001.
  - **f275 TITLE:** 11.00 (flux 10.99, -0.25 frames).
  - The other hits are as in v001; none is more than one frame off.
  - The f137 dip and f141 pickup now fall inside the silence.
- **A/B spectrogram** (qc/AB_spectrogram_v001_vs_v002_src116.0-119.5.png):
  - The edit edges are clean, with no broadband clicks.
  - From 118.70 the spectrum matches v001.
  - The 80 ms fade cuts into a sustained ~600 Hz tone, so the silence begins as a deliberate stop rather than a natural decay, as specified.

## How
- `ffmpeg -i source/trailer.mp4 -vn -af "aresample=48000:resampler=soxr:precision=28,atrim=112.10:127.10,asetpts=PTS-STARTPTS" -ac 2 -c:a pcm_f32le bed.wav`
- `vfx-python scripts/bed_edit.py bed.wav bed_v002.wav` (the gain curve)
- `vfx-python scripts/master.py bed_v002.wav mix_master.wav -1.5 -14.0`
  - +0.10 dB static gain plus a 4x-oversampled 10 ms lookahead peak limiter.
  - Max gain reduction is 1.39 dB, on 1.03% of samples, only on the loudest peaks. The TITLE hit loses about 0.95 dB.
  - I did not use master_audio.sh, because its dynamic loudnorm fallback would reshape the silence.
- QC files: qc/qc_envelope_cues_v002_vs_v001.png, the A/B spectrogram, the AAC test encodes, and qc/transcripts/.
  - 26 JSON files for 28 runs: the windows [0-15] and [0-3.5] share a filename. whisper_gate.txt has all 28 results.

## Notes for picture
- Mograph needs no changes, per the director.
- The silence now starts at f130, not f159. Any on-screen "silence" timing should take that into account.
