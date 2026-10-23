# sh010 color v001 (colorist)
- LUTs (65^3, built by make_luts.py, OKLab maths): tritone.cube (A01-A13, echo bands), drain.cube (C00: tritone, 35% chroma, -0.3 EV pre-map so the floor stays #14080F),
  band.cube (generic unlock, no shot trim), band_<ID>.cube (B01-B08: the unlock + the shot's own OKLab cast trim; used for the graded plates), title_lineup.cube, logo_gold.cube.
- Band order: blue re-hue first (monotonic hue warp, +35 at cyan to +56 on blue, landing at 321-342 = violet-mulberry; chroma x0.7), then the shot cast is removed in OKLab (b axis, plus a only if green) + a small warm offset toward Saffron, then green/olive -> ochre, skin sat 1.15, S-curve, Aubergine floor, Ki White roll-off.
  Why: RGB gain balance or a plain +35 turned blue into teal/green (the board's B01 problem) or left B > R.
- Chains: chains.json (exact -vf per plate). Tritone/drain: luma grain noise=c0s=7:c0f=t BEFORE lut3d so the grain stays on the palette ramp. Encode: x264 crf 10 yuv444p bt709 tv.
- Plates: python3 grade_plates.py (re-grades any plate whose source is newer). QC: python3 qc_rgb.py plates/*.mp4. All 22 pass R >= B (min margin +6 on B03 and C00).
- Title: make_title.py -> title/lineup_tritone.png, title/sf_logo_gold.png (alpha kept, 6% bloom on the logo).
- Known: B01's floor keeps a faint low-chroma khaki. Tritone plates have <=1.2% pixels a few code values under the #14080F luma floor because of grain and YUV rounding.
