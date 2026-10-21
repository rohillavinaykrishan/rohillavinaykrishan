# sh010 mograph v001 - "PARALLAX" (HyperFrames 0.8.181)

- Project: this folder. `index.html`, 2160x3840, 25 fps, 15.0 s (375 frames). Native 4K DOM/canvas, no upscale.
- `prep.py` (run before every render): re-reads `source/credits.txt` -> `assets/credits.js`; copies
  `color/v001/bg_plate_1080.mp4` (only if exactly 375 frames, else the placeholder in `assets/ph/`) and
  `color/v001/sf_logo_silver.png`; converts `roto/v001/points.json` (4K screen px + camera depth Zc, f 2600) -> `assets/points.js`.
- One GSAP driver tween calls `render(t)`; t is quantised to the frame. Every visual (camera, names, canvas) is a pure function of t.
  No requestAnimationFrame, no unseeded random (mulberry32 seeds).
- Camera: pinhole f 2600, principal point (1080,1920). Catmull-Rom path through the treatment keys with an eased global time
  warp 1.5-9.2 s; 9.2-10.84 blends to the solved frontal pose with s(t); frame 271 = exact solved pose (s = 1).
  Path keys were re-tuned from the treatment so the field fills the frame:
  2.0 (100,600,4400) / 6.04 (-500,150,1500) yaw 13 / 9.2 (-1650,-60,2600) yaw 33 pitch 5 (aims the oblique view at the list).
  Unsolved offsets dx +-1150, dy +-1500, dz [-5200,+1400] (her: dz -4800). Drive-hit dolly impulses +60 units.
- Names: DOM text (Archivo 500), each placed with a 2D affine matrix from 3 projected corners (true perspective foreshortening).
  Layout scale L is computed so the real two-column list fits the frame while centred on SUKANYA DILIP DHARIYA
  (her name at frame centre on 271; gutter +-45*L, pitch 96*L; L ~ 0.65 -> list names ~37 px at 4K).
- Canvas: lens grid (k1 -0.22 -> 0, 0.49-1.85 s), lime residual vectors + "+" markers (zero at 271), point cloud 9.2-11.3 s
  unprojected at the solved pose (registers exactly on the plate at 271).
- Title: Bodoni Moda 500 (auto-fit, widest line <= 1760 px, min 150 px), Archivo 125% role/studio, lime rule, lime "+" signature.
  Silver logo revealed on frame 325 by an anamorphic streak mask sweep (8 frames). HUD IBM Plex Mono 38 px (spec 30, raised for phone).
- Fonts in assets/fonts from Google Fonts. GSAP local in assets/vendor.

## Final render (v001)
- Inputs at render time: color/v001/bg_plate_1080.mp4 (375 fr, byte-identical copy), color/v001/sf_logo_silver.png (final),
  roto/v002/points.json (built from the frame-271 image; verified to land on her face on plate frame 271), credits.txt re-read
  (46 rows / 91 names; row 1 SAMITH SOUMYANATH | SIDDHANT SUNIL SONAWANE confirmed by edit/v001/credits_row1_check_58.0s.png).
- Drive-hit impulses use sound/v001 measured onsets (2.8, 3.355, 4.65, 6.043, 7.8, 8.126, 8.711).
- P1 plate opacity opens at 0.95 (frame 0 plate is dim) and settles to 0.70 by 1.4 s; title plate 0.34 (spec 0.28) so Chun-Li reads in the window.
- HUD moved to y 3130 (spec 3020) so it never collides with the bottom list row at the solve; still above the bottom 600 px.
- Command: `python3 prep.py && npx hyperframes@0.8.181 render -q delivery -f 25 -o render/sukanya_mograph_4K.mp4 .`
  6 m 12 s, beginframe capture, software GPU (log: render/render.log). No fallbacks were needed.
- Output: render/sukanya_mograph_4K.mp4, H.264 yuv420p 2160x3840, 25 fps, 375 frames, 15.000 s, no audio.
- Known: the HUD reads "91 TRACKS" (counted from credits.txt; the treatment said 89, but the file holds 91 names).
