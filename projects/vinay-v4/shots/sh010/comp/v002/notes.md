# sh010 comp v002 (supervisor notes_sh010_v4 note 4 + note 2 ghosting). v001 kept.

Same CG / shadow / matte chain and outputs as v001 (see ../v001/notes.md). Rebuild: `bash comp.sh [prep|comp|encode|all]`.

## Note 4: plate macroblocking
- The letterbox crop starts at y=92 (92 mod 8 = 4), so the trailer's 8x8 block grid is 4 rows off in plate_graded, and
  stock deblock/pp never touch the horizontal block edges. Fix at 1280x536 BEFORE the grade and upscale:
  `format=yuv444p,pad=1280:540:0:4,deblock=filter=strong:block=8,crop=1280:536:0:4,hqdn3d=1.5:1:3:3`, then the colorist's
  own finish_filter_v002.txt (LUT + luma grain; reproduces plate_graded bit-exactly), then lanczos + cas 0.55 as before.
  The grain is re-added after the denoise, so it is not eaten.
- Measured on s4/12/23/31/40 (8-px boundary gradient / interior; 1.0 = no blocking): source 1.13, unaligned deblock 1.03,
  pp 1.12, aligned (chosen) 0.92, aligned 2-pass strong 0.77 (over-smoothed). Texture (hf std, lower half) 6.78 -> 6.61.
- Remaining: some 16x16 DC steps inside the flat black suits (s4, s31).
- plate_band_2160x904 uses the same cleaned plate.

## Note 2: ghosting at f169-172
- Cause: the render's motion blur (shutter 0.5) on a 1.5-2.2 m/frame fall; median CG alpha on the monument is 0.75/0.63/0.56/0.68
  on s1-s4 (1.0 from s5). It is not from the comp or the matte.
- Comp fix (s1-s4 only): a' = 1-(1-a)^k, k from each frame's median alpha (2.17/3.05/3.62/2.65) -> body ~95% opaque; the
  smear length and direction are unchanged.
- Limit: at s2-s3 the vertical smear is about one letter-line tall, so the name is solid but not legible during the fall.
  A readable name on f170-172 needs a lighting re-render of s0-s4 with a short shutter (~0.1-0.15, ~5 frames, ~8 min).
  comp.sh picks it up unchanged.

## QC
Lock s4-s43 max 0.49 plate px (CG unchanged). Mattes = roto v001 final (md5 matches v001's run). Sheets: review/comp_v002.png,
review/comp_v002_deblock_ab.png. All movies: 52 frames, 25 fps.
