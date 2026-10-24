# sh010 colour v002 (director quality notes 13 + 14). v001 is kept as it was.

## Note 13: plate grade
- **LUT:** `sunbleach_v002.cube` (33^3), built by `make_lut.py`.
  - saturation 1.00
  - greens (hue 50-185) at 0.85 with a 50% hue shift toward sage (72 deg)
  - skin and the red suit (hue 335-25, fading out by 33 so sand at 34-40 is untouched) at 1.08
  - contrast curve (Hermite):
    - 0 -> 0, which maps to Ink #12100D
    - toe 0.10 -> 0.07
    - slope 1.08 at 0.5, where 0.5 -> 0.585 (this is where the exposure lift comes from)
  - then the v001 tanh shoulder (0.72), then the Ink -> Bone map
  - no gamma (1.0), so the toe lands exactly where the note asks
- **Grade command:** `finish_filter_v002.txt` (LUT, then luma-only grain c0s=5). Input is `../v001/plate_src/plate.%04d.png` (trailer frames 2982-3033, crop 1280:536:0:92); output is `plate_graded/plate.0000-0051.png`.
- **QC (`qc.py`, all 52 frames):**
  - mean Y vs source: +3.8% to +6.1% (target +3% to +8%)
  - B <= G <= R on the whole frame and on the sky
  - VAVG 137-140
  - 0 fails
- **Side effect:** the lower mids get steeper (peak slope about 1.45 around 0.25-0.4). This is unavoidable when the toe goes down while mean Y goes up.

## Note 14: credits duotone
- **Clip:** `credits_graded_v002.mp4`, 720x1280, 25 fps, 69 frames (movie 67.40 s).
- **Filter chain:** `credits_filter_v002.txt`
  - hue=s=0
  - curves master `0/0 0.30/0.08 0.55/0.80 1/1`
  - per-channel map: black -> Umber #2A211A, white -> Bone #F2EBDF
  - bottom 32% fades to Ink (y 870 -> 990), same as v001
- **Map change:** I used black -> Umber instead of the Ink -> Bone map. The note 14 curve crushes the red background to 0, so with an Ink -> Bone map the background would come out Ink, not Umber.
- **Measured** at 0.2 / 1.8 / 2.6 s:
  - text pixels (source grey >= 200, rows 290-860): 100% at Y >= 220, median Y 234
  - background: 41/30/24 (target 42/33/26)

## Review sheet
Before/after: `review/look_test_v002.png` (source | v001 | v002 on s0/s25/s51, plus the credits). It is also copied to `projects/vinay-v4/review/look_test_v002.png`.
