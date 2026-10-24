# sh010 comp v001 (treatment 9.5 + director note 18)

Rebuild: `bash comp.sh [prep|comp|encode|all]` (all upstream paths inside). Per-frame chain: `scripts/comp.py` (header lists it).
Inputs: color/v002/plate_graded (0000-0051 = s0-s51), lighting/v002 cg/shadow/mist (distorted with layout distort.py
--width 2808 --overscan 1.16), roto/v001/matte FINAL (2560x1072, written 14:14; resized to 2808x1176 linear).

## Chain (2808x1176)
- Plate: lanczos 2.19x + cas 0.55 (no unsharp). Upscale verified pixel-centre aligned (0.05 px) with distort.py.
- CG: plate LUT sunbleach_v002 at 40% mix (100% double-lifted the CG: faces 0.72 of sunlit sand; 40% -> ~0.63, inside
  note 17's 55-65%), premult gblur sigma 0.7, alpha-weighted chroma blur 1.4, black lift to Ink, mist haze 3% to the plate's
  sky colour.
- Holdout: CG x (1 - matte); shadow and bloom also held out. Fighters always in front.
- Shadow: d = 1 - luma(catcher) x 1.17, cap 0.78, Umber-tinted multiplier in linear light (core multiplier 0.28 at s25 =
  density ~0.72; R>G>B).
- Light wrap: 4% blurred-plate screen over the monument + edge wrap 0.3 (sigma 3 edge, sigma 10 bg).
- Rim bloom: fixed threshold = 92nd pct of graded CG luma (0.668), blur 12, screen 35%.
- Luma-only grain: the colorist's noise c0s=5:c0f=t on 50% grey through the same upscale (hf std 3.05 vs plate sky 2.9).
- CG band: CG + Umber shadow over #6E665C, same degrade + bloom, no holdout.

## QC
- Lock (scripts/qc_lock.py): plinth front corners vs anchor.json, s4-s43 max slide 0.49 plate px (PASS); constant offset
  <0.4 px. s0-s3 falling (n/a); s44-s51 end whip <0.6 px, except s50 FR x -3.9 (motion-blur edge measurement).
- Shadow direction: the cast shadow runs to the lower-left like the fighters' real shadows (it is strongly foreshortened, a
  thin strip ahead of the plinth, because of the low camera).
- Edges: CG layer over black/white (s25, s38) has no fringes. Contact sheet: review/comp_v001.png.
- All movies: 52 frames, 25 fps.
