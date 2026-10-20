# QC v3 final: Team Lead technical QC
Files:
- `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v3_4K.mp4` (4K)
- `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v3_share.mp4` (share)

Date: 2026-10-20. Contact sheet: `review/qc_v3_final.png`. Evidence crops and logs: `review/qc_v3_final_evidence/`.

## VERDICT: FAIL (minor). One audio spec item is out, and it can be fixed with an audio-only remux.
Every picture item passes. The only failure is true peak. It is 0.04 dB over the ceiling on the 4K file and 0.09 dB over on the share file. AAC encoding overshoot causes it. The picture does not need to be re-encoded.

| # | Item | 4K | Share |
|---|---|---|---|
| 1 | Resolution / codec | PASS | PASS |
| 2 | 25 fps CFR, 375 frames, 15.00 s | PASS | PASS |
| 3 | A/V start 0 | PASS | PASS |
| 4 | Loudness -14 LUFS | PASS | PASS |
| 5 | True peak <= -1 dBTP | **FAIL (-0.96)** | **FAIL (-0.91)** |
| 6 | No black / duplicated / dropped / corrupt frames | PASS | PASS |
| 7 | Intentional freeze 299-306 only | PASS | PASS |
| 8 | No blue-cast frames | PASS | PASS |
| 9 | Spelling (hero, role, show, studio) | PASS | PASS |
| 10 | Roll names match source/credits.txt | PASS | PASS |
| 11 | Lock (255) on the hit, +-1 frame | PASS (see note) | PASS |
| 12 | Slam (307) on the drop, +-1 frame | PASS | PASS |
| 13 | "ROUND ONE!" audible at 1.5-2.6 s | PASS | PASS |
| 14 | No synthetic chimes / tings | PASS | PASS |
| 15 | Type sharpness, frames 290 and 340 at 100% | PASS | PASS |
| 16 | Reels safe zones (top 250 / bottom 600 at 4K) | PASS | PASS |
| 17 | Artist notes.md with commands | PASS | PASS |

## Evidence

1. **ffprobe.** 4K: h264 High, 2160x3840, yuv420p, BT.709, progressive. Share: 1080x1920, same settings. Both have audio AAC LC 48 kHz stereo (4K at 307 kb/s, share at 192 kb/s).
2. **Timing.** Both files: r_frame_rate = avg_frame_rate = 25/1, nb_frames = 375, duration 15.000000. All 374 packet PTS deltas are exactly 0.0400, so the files are CFR with no gaps. `ffmpeg -xerror` decodes both with 0 errors.
3. **Start times.** The video and audio streams have start_time 0.000000. The edit list (media time 1024) only trims AAC priming. Cross-correlating the delivered audio against `sound/v003/mix_master.wav` gives an offset of 0.0 ms on both files.
4. **Integrated loudness.** Measured with ebur128: 4K -14.0 LUFS, share -14.1 LUFS, LRA 3.3 LU.
5. **True peak.** Measured with loudnorm and with 192 kHz astats:
   - 4K: **-0.96 dBTP**. ebur128 rounds this to -1.0.
   - Share: **-0.91 dBTP**. ebur128 shows -0.9.
   - Source master wav: -1.04 dBTP. The ~0.1 dB of headroom was lost in the AAC encode.
   - **Fix:** re-limit the master to a -1.5 dBTP ceiling, or re-run `master_audio.sh` with TP=-1.5 so that the integrated level stays at -14.0. Then remux both files with `-c:v copy -c:a aac -b:a 320k/192k`. Measure TP on the remuxed mp4 and confirm it is <= -1.0.
6. **Frame checks.** blackdetect (d=0.04, pix_th=0.05) and blackframe (95%) found nothing on either file. The darkest frames are 0-22 at mean luma 11.2/255: Ken in the light shaft, visible as intended. framemd5 finds no byte-identical frames. Every consecutive-frame difference outside 300-306 is >= 1.16/255 mean abs, so nothing is duplicated or dropped. Both files have identical per-frame statistics.
7. **Freeze.** Frames 300-306 differ from the previous frame by only 0.62-0.65/255, which is grain and the header fade. This is the plate freeze on frame 299. The roll and the hero name hold through it. freezedetect at -60 dB found no other freezes.
8. **Colour.** Per-frame mean B-R is negative on every frame of both files. The worst values are -25.3 (4K) and -25.5 (share). The look stays warm red/gold throughout.
9. **Spelling (100% crops).**
   - `VINAY KRISHAN ROHILLA` is checked at frames 230, 255-258 and 290 (`t290.png`, `lock.png`) and as the title at 340 (`t340.png`).
   - `SR. MATCHMOVE ARTIST`, `STREET FIGHTER · DNEG` and `TRK_07  SOLVED` are all correct.
10. **Roll names.** I read every visible roll name at 100%:
    - Frame 60 covers S rows 0-4, T rows 6-11 and U row 13 (`r60a.png`, `r60c.png`).
    - Frame 230 covers U and V rows 13-30 (`r230a.png`, `r230b.png`).
    - All of them match `source/credits.txt` character for character, including TRIPURAMALLU KOTESWARARAO, TEJAL CHANDRAKANT KHOCHARE, VIJESH RAMMANI SHARMA, VISHWAS V MARATHE, VIVEK R S and VUYYUR JAYANTH.
    - The Y and Z groups (rows 32-38) never enter the roll window. The roll stops at the lock, as the treatment specifies, so nothing is misspelled there; those names simply are not shown.
11. **Lock.** The spectral-flux onset is at **10.181 s** and the loudest RMS is at 10.24-10.27 s. On screen, frame 255 still shows the unsnapped TRK_07 box. The brackets, gold fill and sparkles first appear on **frame 256 (10.24 s)** and `TRK_07 SOLVED` shows on 258 (`lock.png`). That is 1 frame after the target and 60 ms after the onset. It is within the +-1 frame tolerance and lands on the RMS peak. Note: the motion design trigger is effectively t=10.20 + 1 frame.
12. **Slam.** The audio stays silent at -33 to -41 dB from 11.97 to 12.26 s. The rise starts at 12.29-12.30 s and the transient is at **12.351 s**. The gold flash peaks on **frame 307 (12.28 s)**, and frame 308 shows the morph into the title (`slam.png`). This passes.
13. **"ROUND ONE!"** I ran an independent faster-whisper (small, en) pass on the delivered 4K audio. It returns one segment, "ROUND ONE!" at 1.52-2.52 s, and no other words (`whisper_4k.json`). The spectrogram shows voiced harmonics at about 1.65-2.0 s and 2.35-2.6 s.
14. **No chimes.** I compared the delivered audio against `source/trailer.mp4` 61-76 s in 0.5 s windows:
    - In 1.5-4.5 s, 5.0-6.5 s, 11.0-12.0 s and 13.0-14.0 s, the correlation is 1.000 and the residual is -32 to -49 dB. The bed is the untouched trailer.
    - The rising tone around 2-3 s and the ~880 Hz tonal line around 11.3-12.0 s are inside the trailer bed itself.
    - The residual elsewhere is explained by the allowed elements. In 0.5-1.5 s and 12.25-12.9 s, 97-98% of it is below 120 Hz (the sub layers). In 7.9-10.5 s it is the focus-pull low-pass plus the punch (120-2 kHz).
    - No added tonal content was found.
15. **Sharpness.** At 100% on frames 290 and 340 (`t290.png`, `t340.png`), the edges are crisp on the Bebas title, the Inter role and studio lines, the bracket lines and the mono label. There is no ringing or blocking. On the share file the type is still clean at 1080 (`sh_text.png`).
16. **Safe zones (4K).**
    - The logo top is at about y 320. The header is at about y 1060, the hero name at about y 1870-1970, and the title block runs from about y 1570 to 2510.
    - Nothing key is above y 250 or below y 3240 (`top374.png`, `bot374.png`).
    - Only the faded, soft-masked roll tails touch y 3240-3300 during 1-2.5 s, and the line-up art sits in the bottom zone. Neither is key text.
17. **Notes.** `shots/sh010/color/v002/notes.md` lists the encode settings, timings, QC numbers and log names. The mograph and sound notes list their build commands.

## Fixes required
1. **True peak (both files).** The 4K file measures -0.96 dBTP and the share file -0.91 dBTP; the spec is <= -1.0. Re-master with a -1.5 dBTP ceiling at -14.0 LUFS integrated. Remux the audio into both deliverables with `-c:v copy`, re-measure them, then re-issue as v3 (audio-only change) or v3a.

## Advisories (not blocking, for the supervisor and editor)
- **A1. Frames 23-24, 118-120 and 166-168:** the plate's light-leak flashes start on a 1-frame hard pop. They do not ramp in (plate frames 22->23, 117->118, 165->166). Because the plate opacity dips on those frames, the comp shows about 2-3 frames of flat red base with no picture. These are not black frames, but they read as hard flashes rather than the 6-frame leaks the treatment calls for (`strip_20.png`, `strip_110.png`, `strip_160.png`, `pstrips.png`).
- **A2. Frame 333->334 (13.32->13.36 s):** there is a hard cut in the background under the title hold. The trailer has its own shot change at about 146.89 s, and that falls inside clip J's range (146.20-147.85). It is visible as a jump in the plate behind the card (`strip_329.png`). It goes against treatment section 4, "no hard cuts". To fix it, trim J to before 146.88 or retime it.
- **A3. Frame 308:** for one frame the old line "VINAY KRISHAN ROHILLA" and the new "VINAY KRISHAN / ROHILLA" overlap mid-morph. This is the intended 2-frame crossfade under the flash and is acceptable at speed.
- **A4.** The line-up art (title card, from 12.3 s) contains some blue costume detail. Frame means stay strongly warm, so there is no blue cast.
