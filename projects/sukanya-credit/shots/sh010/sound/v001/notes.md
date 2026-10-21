# sh010 sound v001 - notes

## What was done
- One continuous real bed: `source/trailer.mp4` 141.000-156.000 s, resampled 44.1k -> 48k, sample-exact cut (720000 samples).
  Fade-in 0-0.12 s (3 frames), fade-out 14.3-15.0 s.
- **No synthetic SFX of any kind.** The optional sub reinforcement in treatment section 10 uses the kit's `impact.wav`, so the client rule bans it. Not used.
- Creative move: mid/side stereo-width collapse. 100% width until 9.20 s (f230), eased to 35% by 10.60 s (f265), held,
  then a 6 ms raised-cosine snap back to 100% that completes exactly at 10.840 s (frame 271).
  Static power compensation (max +0.58 dB) means there is no level dip. Measured vs the no-width version:
  - 10.6-10.84 s: side/mid -15.2 dB vs -6.3 dB; L/R correlation 0.94 vs 0.61.
  - RMS difference: average -0.24 dB, worst 0.55 dB (40 ms windows). Identical everywhere outside 9.2-10.84.
  - Plot: `work/verify_width.png`.

## Listen-check 146.9-147.2 s (the logged "You")
Verdict: **a drum hit, not a voice.** No intelligible dialogue.
- The event is a broadband transient with half-rise onset at 147.043 (bed t 6.043) and peak at 147.045. This is the loudest drum in the cue.
  Plots: `work/spec_zoom.png`, `work/spec_144-150.png`.
- Whisper does not agree with itself:
  - small, 146.4-147.8 s: "This is at the point." (no_speech 0.79, word probabilities 0.19-0.96).
  - small, 144-150 s: nothing.
  - medium, 144-150 s: "Five, four, three, two, one." (a classic music hallucination).
  - medium, 146.4-147.8 s: nothing.
  - base, 146.9-147.2 s alone: nothing.
  - A real line would be stable across models and windows.
- The trailer picture at 146.3-147.1 is the arena fight (fighters mid-move, crowd), with no talking face.
- Caveat: the mid channel carries pitched, centred harmonic stacks all through 145.6-148.5 (swoops and stabs repeating with the arrangement).
  This is musical/vocal-like texture, and Silero VAD flags it as speech-like. If any of it is a human effort sound, it is part of the
  trailer's music mix, which treatment section 2 accepts. No words are present.

## Hit times (10 ms check: 5 ms RMS, 1 ms hop, half-rise onset)
| cue | onset (bed t) | peak | frame | trailer t |
|---|---|---|---|---|
| first hit 0.49 | 0.488 | 0.497 | 12 | 141.488 |
| **hero 10.84** | **10.838** | **10.847** | **271** (attack starts 2 ms before the frame boundary, peak inside f271) | 151.838 |
| **title 13.01** | **13.012** | **13.016** | **325** | 154.012 |
| 6.04 loudest drum | 6.043 | 6.045 | 151 | 147.043 |
| 2.80 | 2.788 | 2.793 | 69 | |
| 7.80 | 7.778 | 7.781 | 194 | |

Director's drive-hit cue times that are off by more than 1 frame (for edit and mograph, if they key motion to them):
- 3.44: measured **3.355** (f83).
- 4.60: measured **4.650** (f116).
- 8.20: measured **8.126** (f203).
- 8.80: measured **8.711** (f217).

There is a pre-build (the trailer flare) at 12.92-12.98 (f323-324) before the title stinger. The master shows 0 samples of lag against the pre-master
(alimiter run with `latency=1`), and the onsets in `mix_master.wav` match the bed to within 1 ms.
Zoom plots: `work/zoom_hero_title.png`, `work/zoom_master_hero_title.png`.

## Master
Chain (`work/master_chain.txt`): +0.28 dB, soxr 4x oversample, alimiter ceiling -1.5 dB (attack 1 ms, release 60 ms, latency-compensated), soxr back to 48k, 24-bit.
- Gain reduction: max 1.37 dB; more than 0.5 dB for 200 ms in total; more than 1 dB for 25 ms. Nothing clipped (sample peak -1.50 dBFS).

| file | LUFS-I | dBTP |
|---|---|---|
| mix_master.wav | -13.99 | -1.50 |
| mix_master_nowidth.wav | -13.98 | -1.50 |

Both files: pcm_s24le, 48000 Hz, stereo, 720000 samples = 15.000 s.

## AAC test encodes (ffmpeg 6.1.1 native aac, `-cutoff 20000`, decoded and measured with loudnorm/ebur128 true peak)
As-is encodes:

| file | AAC 320k | AAC 192k | AAC 192k `-aac_coder fast` |
|---|---|---|---|
| mix_master.wav | -14.05 LUFS / **-1.46 dBTP** | -14.11 / **-1.42** | -14.07 / -1.28 |
| mix_master_nowidth.wav | -14.04 / -1.46 | -14.11 / -1.30 | -14.06 / -1.28 |

**Robustness warning (important for comp/delivery).** The native encoder at 192k (default twoloop coder) sometimes overshoots by 1-2.5 dB on the hardest drum transients (6.06, 3.26, 13.01 s).
Whether it does depends on AAC frame alignment. I tested 16 sample offsets (0-960 samples of leading delay):
- 192k default: fails at **4/16** offsets (worst +0.67 dBTP for mix_master, +0.98 for nowidth). In an earlier pass at a slightly different gain, the nowidth file failed as-is (-0.24).
  Lowering the ceiling to -2.0 or -2.5 dB does NOT fix this (a -2.5 ceiling still produced -0.36).
- 192k `-aac_coder fast`: 0/16 fails, worst -1.03.
- 320k default: 0/16 fails, worst -1.32 (mix_master) / -1.39 (nowidth).

Recommendation for the mux:
- 4K master: `-c:a aac -b:a 320k -cutoff 20000`.
- <16 MB share copy: `-c:a aac -aac_coder fast -b:a 192k -cutoff 20000`.
- Mux the WAV as-is (start at 0, no re-trim/resample), and re-measure the true peak of the final mp4 audio.

## Commands
Scripts used (numpy/scipy via vfx-python): width/mix build, onset measurement, spectrogram and verify plots. The working files are in `work/`
(`bed_raw.wav`, `mix_width.wav` = pre-master, `mix_nowidth.wav`, `width_cfg.json`, `onsets_raw.json`, `onsets_master.json`, the transcripts `chk_*.json`).
