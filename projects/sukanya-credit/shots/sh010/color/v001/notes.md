# sh010 color v001 - "SILVER and LIME" plate grade + silver logo

## silver.cube (65^3, make_cube.py)
- Output depends only on a panchromatic luma Y = 0.45*Rec709 + 0.55*max(RGB). With pure Rec.709 luma the blue/neon shots
  (P7, P8, P9) went muddy-black because blue only carries 7% weight. The max(RGB) term keeps coloured light reading as light.
- Tone curve (PCHIP): 0->0, .06->.012, .12->.038, .30->.262, .50->.50, .70->.735, .85->.90, 1->.97 (crushed toe, soft shoulder, paper white .97).
- Ivory toning is weighted to the highlights only (smoothstep .35-1.0 toward #F4EFE6 ratios 1/.98/.943). Shadows and mids are exactly neutral,
  and B <= G <= R always holds, so no output pixel can be blue.

## finish_filter.txt (one ffmpeg -vf chain, used on the 1080x1920 raw plate)
gblur 1.2 -> vignette PI/5 -> lut3d silver.cube (tetrahedral) -> yuv420p -> noise c0s=7 temporal+uniform on LUMA ONLY (chroma planes untouched) -> bt709 tags.
Changes from the treatment chain: the grain is luma-only (`noise=alls` would add chroma grain), the vignette is PI/5 rather than PI/4.5 (P1/P9 are very dark),
and the curve has a slightly lifted low-mid so frame 0 shows Chun-Li clearly.
Usage: ffmpeg -i in.mp4 -vf "$(cat finish_filter.txt)" -c:v libx264 -crf 14 out.mp4   (the LUT path inside it is absolute)

## sf_logo_silver.png (make_logo.py)
2160x1151 RGBA, straight alpha. Built from assets_from_vinay/sf_logo_alpha.png: Lanczos upscale of premultiplied RGB, alpha <0.03 -> 0,
specks/islands <400 px removed (5 of 18 dropped), RGB=0 where alpha=0. Tone = continuous chrome profile across each text line (bright top, dark
horizon at ~58%, lift at the bottom) + source grit (luma high-pass) + a bevel from the alpha distance field, lit from the upper left with specular,
mapped #1A1A1C -> #F4EFE6. No red/orange survives. Checked over black and white (review/logo_silver_check.png).

## Plate
Input: edit/v001/bg_plate_raw_1080.mp4, graded from a snapshot copy after the editor's rebuild finished (the first attempt read a file that was
still being rewritten -> truncated, and was replaced). Output written to work/ and then moved into place atomically.
