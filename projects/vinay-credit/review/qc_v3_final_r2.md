# QC v3 final, round 2 (re-delivery 2026-10-21 13:05/13:06): Team Lead technical QC
Files (overwritten at the same paths):
- `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v3_4K.mp4` (166.3 MB)
- `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v3_share.mp4` (13.7 MB)

Inputs: mograph v003 + plate edit v005 + sound v004, conformed in color v003.
Contact sheet: `review/qc_v3_final_r2.png`. Evidence: `review/qc_v3_final_r2_evidence/`. This report supersedes `review/qc_v3_final.md`.

## VERDICT: PASS
The round-1 failure (true peak) is fixed, and every item on the QC list passes on both files. The advisories at the end are non-blocking.

| # | Item | 4K | Share |
|---|---|---|---|
| 1 | Resolution / codec | PASS | PASS |
| 2 | 25 fps CFR, 375 frames, 15.00 s | PASS | PASS |
| 3 | A/V start 0, sync to master | PASS | PASS |
| 4 | -14 LUFS | PASS (-14.0) | PASS (-14.1) |
| 5 | True peak <= -1.0 dBTP | **PASS (-1.43)** | **PASS (-1.36)** |
| 6 | No black / duplicated / dropped / corrupt frames | PASS | PASS |
| 7 | Freeze only at 299-306 (plus the documented plate tail hold, see A2) | PASS | PASS |
| 8 | No blue cast | PASS | PASS |
| 9 | Frames 20-28, 116-124, 164-172: footage visible, ramps, no flat frames | PASS | PASS |
| 10 | Frames 325-374: no background jump | PASS | PASS |
| 11 | Frames 305-312: one typeface per frame | PASS | PASS |
| 12 | Trackers 197-255 at phone size | PASS | PASS |
| 13 | Spelling + roll names = credits.txt | PASS | PASS |
| 14 | Lock 255 / slam 307 sync (+-1 frame) | PASS | PASS |
| 15 | "ROUND ONE!" audible, no chimes | PASS | PASS |
| 16 | Type sharpness at 100% (frames 290 and 340) | PASS | PASS |
| 17 | Reels safe zones | PASS | PASS |

## Evidence
1. **ffprobe.**
   - 4K: H.264 High, 2160x3840, yuv420p, BT.709, progressive.
   - Share: 1080x1920 with the same settings.
   - Audio: AAC LC 48 kHz stereo, 306 kb/s on the 4K and 192 kb/s on the share.
2. **Timing.**
   - Both files: r/avg frame rate 25/1, nb_frames 375, duration 15.000000.
   - All 374 PTS deltas are exactly 0.0400 s.
   - `-xerror` decode gives 0 errors.
3. **Start and sync.**
   - Video and audio start_time are 0.000000 on both files.
   - Cross-correlating against `sound/v004/mix_master.wav` gives an offset of 0.0 ms on both files.
4. **Loudness.**
   - ebur128: 4K -14.0 LUFS, share -14.1 LUFS, both with true peak -1.4 dBFS.
   - loudnorm meter: 4K TP -1.43 dBTP, share -1.36 dBTP, LRA 3.4.
   - Both are under the -1.0 ceiling with 0.36 dB or more of margin.
5. **Frames.**
   - blackdetect (d=0.04, pix_th=0.05) and freezedetect (-60 dB) find nothing on either file.
   - framemd5 finds no byte-identical frames.
   - The minimum mean luma is 11.2/255 on frames 0-22. That is Ken in the light shaft, intended and visible.
6. **Freeze.**
   - Frames 300-306 change by only 0.62-0.65/255 per frame. That is grain plus the header fade, as intended.
   - Outside the freeze, every frame changes by at least 1.07/255, except the plate tail hold at 354-374 (see A2).
7. **Colour.** Per-frame mean B-R is negative on every frame. The worst values are -25.4 on the 4K and -25.3 on the share.
8. **Leaks.** The per-frame change through each leak is now a smooth ramp, with no single-frame jump (`strip_18.png`, `strip_112.png`, `strip_124.png`, `strip_162.png`):

   | Leak | Per-frame change (/255) | Round 1 |
   |---|---|---|
   | 20-28 | 1.7 → 3.1 → 3.6 → 7.1 → 6.5 → 8.3 → 9.3 | 75.6 at frame 23 |
   | 116-124 | 7.1-14.7 | 28.3 at frame 118 |
   | 164-172 | 4.3-8.2 | 29.4 at frame 166 |

   Footage is visible on every frame: Ken's hand through 24, the glove punch under the right-side leak at 118-121, and the scream under the top-right leak at 166-171. No frame shows flat red base only.
9. **Frames 325-374.**
   - The largest per-frame change is 2.35/255 (it was 78 at the 333→334 cut in round 1).
   - Plate v005 runs J 146.104-146.840 at 0.40x, so it never reaches the trailer's own cut at 146.897.
   - scdet (threshold 10) on the plate finds only frame 307 (`strip_tail.png`).
10. **Frames 305-312** (`swap.png`, `strip_303.png`).
    - 305-306: the locked Inter name with brackets and "TRK_07 SOLVED", as before.
    - 307: radial gold bloom only. No name, brackets, label, trackers or roll.
    - 308: Bebas title only, blurred and scaled.
    - 309-312: the Bebas title resolves.
    - No frame contains both the Inter name and the Bebas title.
11. **Trackers 197-255.**
    - Phone-size view (share scaled to 405x720, `trk_phone.png`): the boxes, "+" centres and red LOST state read clearly. The TRK labels are fine print, which is acceptable for the secondary HUD.
    - At share 1:1 (`trk_share_1to1.png`): the labels read cleanly, e.g. "TRK_06 LOST" and "TRK_07".
    - TRK_07 stays on VINAY KRISHAN ROHILLA through 255.
12. **Spelling** (4K, 100% crops `r60.png`, `r230a.png`, `r230b.png`, `t290.png`, `t340.png`).
    - Every visible roll name matches `source/credits.txt` exactly: S, T and U groups at frame 60, U and V rows at frame 230.
    - Correct: VINAY KRISHAN ROHILLA (roll, hero, title), SR. MATCHMOVE ARTIST, STREET FIGHTER · DNEG, TRK_07 SOLVED.
13. **Sync.**
    - Lock: the audio onset is at 10.181 s. Frame 255 still shows the plain TRK_07 box. The snap, gold fill and sparkles appear on frame 256 (10.24 s), and SOLVED on 258 (`lock.png`). That is +1 frame, inside the tolerance, and on the loudest part of the hit. Same as round 1.
    - Slam: silence (-33 to -41 dB) until 12.27 s, rise at 12.29-12.30 s, transient at 12.351 s. The bloom peaks on frame 307 (12.28 s). PASS.
14. **Audio content.**
    - faster-whisper (small, en) on the share audio returns only "Round one!" at 1.52-2.52 s. Round 1 got the same result on the 4K.
    - Compared with trailer 61-76 s, the delivered audio matches it exactly (correlation 1.000, leftover -27 to -50 dB) everywhere except the accent windows.
    - In the accent windows, the extra energy is 95-98% below 120 Hz (the sub layers) at 0.5-1.5 s and 12.25-12.9 s, and the punch plus the focus-pull filter at 10.1-10.5 s.
    - No synthetic chimes or tones were added.
15. **Sharpness.** At 100% on frames 290 and 340, the edges are crisp on Bebas, Inter, JetBrains Mono, the brackets and the rule. There is no ringing or blocking.
16. **Safe zones (4K).** Layout is unchanged from round 1. The logo top is at about y 320 and the title block spans about y 1570-2510. Nothing key is above y 250 or below y 3240. The trackers sit inside the roll window.

## Advisories (non-blocking)
- **A1. Trailer-internal cuts are still in the plate** (`pcuts.png`). These are cuts the trailer itself contains, inside the source ranges of clips B, D and E, not edits we made:

  | Frames | Clip | Trailer cut | Status |
  |---|---|---|---|
  | 36→37 | B | 38.29 | Documented in the EDL as deliberately placed on beat frame 38. It actually lands 1 frame early. |
  | 113→114 | D | about 41.62 | Not documented. Lands 6 frames before the 4.8 s beat. |
  | 133→134 | E | about 50.6 | Not documented. |

  They are the same kind of cut that was removed from J. They are not defects, and the roll covers them, but in an edit that is meant to have no hard cuts they read as extra cuts. If the supervisor wants them gone, D and E can be retimed the same way as J.
- **A2. Frames 354-374 (14.16-15.00 s):** the plate holds a still frame for 21 frames under the poster card. This is by design (EDL `changes_v004`: "0.40x + tail freeze"). The card push-in and embers keep the frame alive (per-frame change 1.1 → 0.41/255). The plate motion stops abruptly at 353→354. It is acceptable for a poster hold, but it is worth knowing if the piece is meant to loop.
- **A3. Process.**
  - `shots/sh010/edit/v005/` has no `notes.md`. Its changes are recorded only in the `edl.json` field `changes_v005` and in mograph v003's notes. The editor should add `edit/v005/notes.md` with the build command and the change list.
  - v3 was overwritten in `deliver/` after a review. Conventions say a reviewed version should never be overwritten, so a v4 name would have kept the round-1 files for comparison.
