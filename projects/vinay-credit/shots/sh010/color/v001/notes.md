# sh010 color v001 - look development "fire-lit dark" (treatment sec. 5)

## Files
- warm.cube            33^3 LUT (DOMAIN 0-1), built by `KBASE=0.58 REDAMT=0.65 GAM=1.06 python3 make_lut.py warm.cube v3`
- make_lut.py          generator (variants: `spec` = literal treatment formula, `v3` = shipped)
- finish_filter.txt    the post-LUT finishing chain (1080 plate), single line
- sheet.sh             contact-sheet helper (before row + one row per LUT)
- frames/A..J.png      one frame per bg shot, active-picture + treatment vertical crop, 540x960
- look_test_v001_3row.png  before / LUT only / LUT + finish
- ../../../../review/look_test_v001.png  before / after (LUT + finish + per-shot trims)

## LUT design (what changed vs. the literal treatment formula)
The literal formula (0.72 gradmap(Y) + 0.28 warm) was tested first: flat monochrome orange, red gi and skin
merge, bright skies/floors go flat pale-gold. Shipped `v3`:
1. Gradient stops exactly as the treatment (#050202 > #3A0D08 > #8E1A0E > #E0581A > #F5B53C > #FFE7B0).
2. Gradient driven by a red-weighted luma Yw = 0.40R + 0.55G + 0.05B (blue/teal sources sink to ember shadow
   instead of glowing gold), gamma 1.06 + gentle S-curve, blacks crushed 2%.
3. Highlight shoulder: from 0.70 the luma rolls off exponentially to 0.94, so white lands on gold/pale gold, never clipped white.
4. Mix 0.58 gradmap + 0.42 warm(original) (warm = 1.02R, 0.86G, 0.55B, luminance-matched to the gradient)
   so texture and skin variation survive; skin-hue pixels (R>=G>=B, sat 0.10-0.70) get 25% less gradmap.
5. Red separation: true reds (G/R < ~0.4 and hue < ~10 deg: gi, gloves, head paint) are pulled 65% toward
   Street Fighter red #C8161D, soft-gated so skin (hue 14-30 deg) is untouched and no macroblock edges pop.
6. Final clamp G <= R, B <= G on every LUT entry (max B-R over the cube = -0.0014).

## Editor: filter string to append (plate at 1080x1920, after the xfade chain)
Per-shot exposure trims, applied to the clip BEFORE the xfade/LUT (optional but recommended):
- A (36.72-37.48, silhouette, otherwise nearly black): `eq=gamma=1.45:contrast=1.05`
- G (123.72-124.28, hot orange scream):                 `eq=gamma=0.85`

LUT + finish (one chain, appended after the last xfade):
```
format=gbrp,lut3d=file=/home/user/rohillavinaykrishan/projects/vinay-credit/shots/sh010/color/v001/warm.cube:interp=tetrahedral,curves=all='0/0 0.12/0.13 0.45/0.51 0.8/0.84 1/0.94',eq=saturation=1.06,gblur=sigma=3,vignette=angle=PI/4.5,format=yuv444p,noise=c0s=6:c0f=t,format=yuv420p
```
- Grain is luma-only (`c0s`) on purpose: RGB/all-plane grain put blue-dominant speckles in the blacks
  (up to 10% of pixels B>R on shot A). Luma-only grain = 0 pixels with B>R.
- `curves` top at 0.94 keeps highlights gold, lifts low mids slightly so the plate is not muddy under the dimming.
- `gblur=sigma=3` is for the 1080 plate (I used 1.5 at the 540 proxy).

## QC (540 proxy frames, LUT + finish, per shot mean RGB 0-255, B-R)
A 6.8/3.2/1.0 (-5.8; 0 px B>R) | B -34.9 | C -41.2 | D -35.5 | E -34.4 | F -44.4 | G -112.8 | H -53.3 | I -45.5 | J -44.8
All shots: 0.0% of pixels with B > R. Skin checked on C (Dhalsim, red head paint stays paint, skin stays warm brown),
E (boxer face), G (scream, amber not plastic), I (leaping fighters). Remaining blockiness in C/E is source
compression at 1.8x crop scale; the sigma-3 blur on the plate hides it.

## For final delivery (later)
- Run `signalstats` on the final: mean(V-U) stays positive / B-R mean negative per frame (treatment QC).
- Deliver: `tools/vfx/bin/grade.sh deliver <conform> deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v3_4K.mp4 uhd-vertical`,
  check 2160x3840, 25 fps, 375 frames, 15.00 s, lock frame 255 / slam frame 307 in sync.
- Do not grade the HyperFrames type layer with this LUT (it would turn ivory names gold); LUT is plate-only.
