# Team Lead QC: v4 FINAL (sh010 "GROUND TRUTH"), 2026-10-22

Files checked:
- `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v4_4K.mp4` (4K)
- `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v4_share.mp4` (share)

Contact sheet: `review/qc_v4_final.png`. It has 21 key frames, the soft-credits crop, the plinth vs anchor crosshairs, the onset waveform/spectrogram plots and the SOLVE HUD.

# VERDICT: FAIL

There are 2 blocking items: 6 (words in the audio) and 9 (soft credit type). Every other gate passes.

| # | Gate | Result |
|---|---|---|
| 1 | Format / timing / loudness / size | PASS |
| 2 | Black, dropped and duplicated frames | PASS |
| 3 | No blue cast; pink only in graphics | PASS |
| 4 | Spelling | PASS |
| 5 | HUD = solve_stats.json | PASS |
| 6a | Sync f173 / f275 | PASS |
| 6b | Whisper: no words | **FAIL** |
| 7 | Monument does not slide (FINAL) | PASS |
| 8 | Title and name type sharp at 100% | PASS |
| 9 | Credits type sharp at 100% | **FAIL** |
| 10 | Reels safe zones | PASS |
| 11 | Notes with commands for delivery | FAIL (paperwork) |

## 1. Format / timing / loudness / size: PASS

**Format (ffprobe):**

| | 4K | share |
|---|---|---|
| Video | h264 High, yuv420p, bt709 tv | same |
| Resolution | 2160x3840 | 1080x1920 |
| Frame rate | 25/1 r and avg | 25/1 r and avg |
| Frames | 375 (counted with -count_frames) | 375 |
| Video duration / start | 15.000 s / 0.000 | 15.000 s / 0.000 |
| Audio | AAC LC 48 kHz stereo, start 0.000, 15.000 s | same |

**Timing:**
- CFR: all 374 pts deltas are exactly 40 ms, in both files.
- A/V: cross-correlating the decoded audio of both files against `sound/v002/mix_master.wav` gives a lag of 0 samples.

**Loudness (ebur128, true peak):**

| | Integrated | LRA | True peak |
|---|---|---|---|
| 4K | -14.0 LUFS | 3.0 LU | -1.4 dBTP |
| share | -14.1 LUFS | 3.0 LU | -1.6 dBTP |

**Share size:** 16,071,978 B = 15.33 MiB, under 16 MiB.
- Note: it is 16.07 MB in decimal units. The treatment says "<16 MB". If the uploader is strict about decimal MB, re-encode at about -3% bitrate.

## 2. Black, dropped and duplicated frames: PASS
- **Black:** blackdetect (d=0.05, pix_th=0.05) finds nothing in either file. Frame 0 is the credits frame (mean luma 45). The darkest frame is f221 (mean 13.6, the breakdown slide-in), which is not black.
- **Exact duplicates:** framemd5 shows no consecutive identical frames, in 4K or share.
- **Near-duplicates:** I measured the mean abs diff between consecutive frames at 540x960. The only dips are the intended holds in edl.json:
  - f120-121: freeze on s51 into TILT
  - f136: end of the tilt
  - f165-166: registration settle onto camera s0
  - f277-374: the title poster push (diff about 0.2 = grain plus a 1.00 to 1.03 push)
- **Freezedetect on the 4K:** only 14.84-14.92 s, inside the poster push.
- **Freezedetect on the share:** repeated short hits from 11.48 s. This is the same slow push falling under the threshold at 1080; there are no identical frames.
- **f65-68 black panel:** the panel inside the band bracket is the designed "roll darkens to Ink inside the bracket" (treatment §7, f60-68). It is not a black frame.

## 3. No blue cast; pink only in graphics: PASS
Mean B ≤ G ≤ R holds on every frame, 375 of 375.

| Region | Mean R / G / B | Min R-G | Min G-B |
|---|---|---|---|
| TRACK band | 159.7 / 131.9 / 110.8 | 19.7 | 18.7 |
| FINAL band | 163.5 / 140.5 / 114.5 | | 22.6 |
| Breakdown bands | | | 2.2 (lowest, band 1) |

- Blue-dominant pixels in the plate acts: 0.0001% or less.
- The "pink" pixels in FINAL are:
  - the act label and caption "+" (x 112-220)
  - the f173 halo
  - the LOCKED tag
  - from f211, the woman's red suit, which is natural plate colour (checked at f215)
- The line-up art in the credits keeps its costume colours, which is allowed.

## 4. Spelling (100% crops): PASS
- "VINAY KRISHAN ROHILLA" is correct in all of these places:
  - the credits row: f0, and f60 on the brush plate in Ink
  - the 3D title: f275-374
  - the CG band
- "SR. MATCHMOVE ARTIST" and "STREET FIGHTER · DNEG" are correct at 100% (f304, f374), and also on the share file.
- **Credits rows:** every visible row matches `source/credits.txt`, from SHEKHAR LAHASE / SURYAWANSHI GOPAL ASHOK through ZANG CHEN (crops of f0, f60, f68).
- **The 3 extra rows above line 1** match the movie.mp4 67.40 s frame exactly:
  - SHASHIKANTH B TUPSUNDAR | SURAJ PANKAJ MISTRY
  - SHATADRU BOSE | SURESH KOTHARI
  - SHEELVANT SINGH | SURYA K

## 5. HUD = solve_stats.json: PASS
- **SOLVE (f160):** every number matches:
  - CAMERAS 52/52 (52/52)
  - POINTS 4,817 (4817)
  - MEAN REPROJ 0.660 px (0.659956)
  - f 998.91 px (998.91)
  - LENS 28.09 mm (28.09)
  - k1 -0.1975 (-0.1975)
- **TRACK:** the per-frame counts match:
  - f82 = s13: TRACKS 0441 matches per_frame[13] = 441; SRC 2995 = 2982+13.
  - f100 = s31: TRACKS 0983 matches per_frame[31] = 983; SRC 3013.
- **FINAL caption:** CAMERAS 52/52.

## 6a. Sync: PASS
- Delivered audio is sample-aligned to the master (lag 0).
- **Landing (f173):** the waveform shows the HERO attack on the f173 boundary (6.92 s), and librosa puts the onset at 6.945 s, which is inside f173. On the picture side the monument falls f170-172, makes contact with the pink halo on f173 and settles on f174.
- **Title (f275):** the attack is at 11.00 s, and the librosa onset is 11.015 s, inside f275. The picture hard-cuts on f275 (diff spike f274 to f275) after the f273-274 fold.
- The other cues are also within one frame: f69 at 2.71 s (f67.75 to f69 boundary), f208 at 8.30 s (f207.5).

## 6b. Whisper, no words in the audio: FAIL (blocking)
The sound department's gate (`sound/v002/qc/whisper_gate.txt`, all empty) ran faster-whisper with `vad_filter=True`. VAD drops vocals that sit under music. I re-ran it on the delivered 4K audio with no VAD, temperature 0, language en and word timestamps:

**The words are the same across models:**
- base: "...make it all the **champion**, it's the key to **knock, knock, knock**"
- small: "...make it down the chain, never let's the game **Knock, knock, knock**"
- medium: "Now I'm the **million dollar champion** and that's the game, **knock, knock, knock**"

Medium word confidences: million 0.71, dollar 0.93, champion 0.90, knock 0.78-1.00. "Champion" lands at 1.32-1.36 s in all three models, and "knock" at about 2.6-3.9 s.

**The vocal is centred (mid/side split, first 4 s):**
- The mid channel, and mid band-passed to 250-4000 Hz, both give the identical lyric with the same timestamps.
- The side channel gives only the classic hallucination "Thanks for watching!".
- That is a centred lead vocal, not a hallucination.

**Source context:** source/trailer.mp4 106-116 s with medium gives "Oops, you dropped something" (110.5-111.3, also detected with VAD on). It then gives "Now I'm the million dollar champion" at 112.0 and "The next to get knocked, knocked, knocked" at 114.0. The bed starts at 112.10.

**Suspected, not confirmed:**
- t 8.6-9.9 s: medium twice gives "(This/It) might sting a little" ("a little" p 1.00). base and small disagree.
- t 3.8-5.2 s: medium mid gives a looping "no, no, no".

**Conclusion:** the bed contains sung or rapped words, at least t 0-4 s (f0-100) under the credits and the cut into TRACK.

## 7. Monument does not slide (FINAL): PASS (spot-check)
- **Visual:** I drew the anchor.json `front_right` plinth corner (x2.19375) on comp/v001/final_2808 at s5, s15, s25, s35, s46 and s51. The crosshair sits at the same offset from the visible plinth's right-base corner in every frame (about 25-30 px right at 2808 scale, on the base line). There is no visible drift.
- **Measured:** an automatic edge measurement locks cleanly on s27-s43. The offset is +24 to +28 px at 2808, a 4 px span, which is about 1.8 px at plate res (about ±0.9 px).
- **Limits:** on other frames the woman's leg or motion blur hides the plinth corner, so the measurement is unreliable there; I relied on the visual crosshair check for those frames.
- **Deliverable:** in the deliverable, mograph applies one transform to the whole FINAL video, so plate and CG cannot slip against each other.

## 8. Title and name type sharp at 100%: PASS
- Crisp at 100%:
  - "VINAY KRISHAN ROHILLA" on the brush plate (f60), and the plate's dry-brush edge
  - the 3D title (f374), with clean bevels and no aliasing
  - SR. MATCHMOVE ARTIST and STREET FIGHTER · DNEG (f304)
- The share file is also sharp at 1080.

## 9. Credits type sharp at 100%: FAIL (blocking, small fix)
Below y ≈ 2700 (4K) the visible credit rows are only the blurred source roll underlay, a 720p upscale with gblur 5, with no native type on top.
- The affected rows run from VIJESH RAMMANI SHARMA / VIVEK R S through VIKAS, VIKASH, the whole Y block and ZANG CHEN.
- They are faint through f0-59 and plainly readable on f60-68, once the line-up art leaves and the bracket flies out.
- The VIJESH row also reads doubled, because the half-faded native type sits over the offset underlay.
- Evidence: the crop of f68 at x 250-1650, y 2700-3200 (on the contact sheet).
- **Cause:** in `shots/sh010/mograph/v001/index.html` the native `.crow` rows fade out with `(1 - ramp(y, 2600, 2790))`. `#credUnder` (opacity 0.3) only has a top mask (`transparent 0-918px`) and no bottom fade, so the blurred rows stay visible where the native ones have faded.

**Advisory (not blocking):** at many row ends the underlay glyphs stick out 20-40 px past the native type as soft ghost letters, because the source glyphs are wider. Examples at f0: a ghost "K" after SURYAWANSHI GOPAL ASHOK, and an "S" before SHIVKUMAR VISHWAKARMA.

## 10. Reels safe zones (4K): PASS

| Element | y position | Limit |
|---|---|---|
| Top HUD (SOURCE / MOVIE timecode) | from 340 | top 250 px |
| Act labels | 1380 | |
| Title logo | top ≈ 360 | top 250 px |
| 3D name | 1250-2180 | |
| SR. MATCHMOVE ARTIST | ≈ 2630 | |
| STREET FIGHTER · DNEG | ≈ 2830 | bottom 3240 |
| SOLVE HUD | ends ≈ 3130 | bottom 3240 |
| Breakdown band labels | inside the bands (band 1 label ≈ y 912) | |

- The only thing in the top 250 px is the credits SF logo at f14-f30 (the source logo, at about y 40). It is branding, not key text.
- The bottom 600 px holds only the line-up art, plate bleed and breakdown band 4 imagery.

## 11. Delivery notes: FAIL (paperwork)
- There is no delivery department folder or notes.md recording the mux and share encode commands (conventions: notes.md lists commands used).
- The mograph and sound notes exist and list their commands.

# Fixes, in order

1. **Sound: remove the vocal (t 0-4 s, src 112.10-116.1) and recheck the rest.**
   - Option A: re-pick a bed section that has no vocals.
   - Option B: install demucs (htdemucs), separate `source/trailer.mp4` 112.10-127.10, and use the `no_vocals` stem through the existing `bed_edit.py` / `master.py` chain.
   - Keep f173 (6.92 s) and f275 (11.00 s) on their attacks.
   - Re-gate Whisper **without VAD**: mid channel and full mix, base, small and medium, windows of 3-4 s. Use the side channel as the hallucination control. Also check t 3.8-5.2 and 8.6-9.9.
   - Remaster to -14 LUFS / ≤ -1 dBTP.
2. **Mograph: add a bottom fade to the credits underlay.**
   - Give `#credUnder` the same bottom fade as the rows, in frame space: multiply its opacity per frame, or add a full-frame overlay mask that goes transparent from y 2600 to 2790.
   - Alternatively, extend the native rows down to the bottom of the roll.
   - Optionally, narrow the underlay's glyph-width mismatch, or drop its opacity to 0.15-0.2 so the ghost letters at row ends go away.
   - Re-render 4K (only f0-68 change).
3. **Delivery:**
   - Re-mux the new audio and video.
   - Re-encode the share copy, below 16.0 MB decimal if the target is strict.
   - Write `shots/sh010/delivery/v001/notes.md` (or similar) with the exact ffmpeg mux and share commands, then re-run this QC.

# Tools / commands used (Team Lead)
- `ffprobe -show_entries format/stream ...`, `-count_frames`, packet pts deltas
- `ffmpeg -af ebur128=peak=true`
- `blackdetect=d=0.05:pix_th=0.05`
- `freezedetect=n=0.001:d=0.08`
- `-f framemd5`
- consecutive-frame diff and per-region RGB means in numpy (540x960 decode)
- `select` frame extraction plus ImageMagick crops and montage
- cross-correlation against mix_master.wav
- librosa onset_detect with waveform/spectrogram plots
- faster-whisper base, small and medium (int8, no VAD, word timestamps) on the full mix, mid and side channels
- plinth crosshair overlay and edge measurement on comp/v001/final_2808 vs layout/v001/anchor.json
