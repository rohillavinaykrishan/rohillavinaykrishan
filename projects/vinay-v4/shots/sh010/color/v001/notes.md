# sh010 colour v001 (colorist)

Plate source: no editor plate existed, so I extracted it myself. Command: trailer.mp4 `select=between(n,2982,3033),crop=1280:536:0:92`, giving plate_src/plate.0000-0051.png (0-based, s0..s51).

## Plate grade: SUN-BLEACHED
- `sunbleach.cube` (33^3, display-referred). It is built by `make_lut.py` and does these steps in order:
  1. gamma 0.98 midtone lift
  2. tanh shoulder from 0.72 (creamy roll-off)
  3. saturation 0.88; greens (hue 50-185 deg) get saturation 0.70 and are hue-shifted 65% toward 72 deg (sage/olive)
  4. per-channel map: black to Ink #12100D, white to Bone #F2EBDF
  Skin, red and orange hues are not touched by the green shift.
- `finish_filter.txt` holds the full chain: LUT (tetrahedral), then luma-only grain `noise=c0s=5:c0f=t` in yuv444p, then rgb24.
  - The grain is on luma only, not the `alls=5` from the treatment, so there is no chroma speckle.
- Re-grade: `ffmpeg -start_number 0 -i plate_src/plate.%04d.png -vf "$(cat finish_filter.txt)" -start_number 0 plate_graded/plate.%04d.png`

## QC (`qc.py`)
Results for all 52 frames:
- Mean Y vs source is +0.9% to +4.4%, inside the ±5% limit.
- Mean B ≤ G ≤ R holds for the whole frame and for the sky (top 60 rows).
- Cr (VAVG) is 135-137, so ≥ 128.
- The sky reads warm bone, about 196/184/168 on s0.

## Credits
- `credits_graded.mp4`: movie.mp4 67.40 s, 69 frames, 720x1280, 25 fps, H.264 crf 10.
- The filter is in `credits_filter.txt` and follows the section 5 recipe exactly. The bottom 32% (from y 870) ramps to Ink by y 990.
- Measured: YAVG 36.7, U 125.9, V 129.1 (warm, no blue).
- The roll background comes out near-Ink rather than a visible Umber, because the 0.45→0.18 curve crushes the red.

## Logo
- `sf_logo_bone.png`: 2160x1151 RGBA.
- Made by `make_logo.py`: the luminance high-pass (brush texture) is mapped Umber→Bone, the low-frequency yellow→red gradient is removed, and the soft edges are forced to Bone.
- Clean over black and white. Opaque mean is 224/216/204.

## Review
- Look test: `review/look_test_v001.png`, also copied to `projects/vinay-v4/review/look_test_v001.png`.
