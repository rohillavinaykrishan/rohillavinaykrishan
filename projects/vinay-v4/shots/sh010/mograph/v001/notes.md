# sh010 mograph v001 - GROUND TRUTH (HyperFrames 0.8.184)
- index.html: 2160x3840, 25 fps, 15.0 s (375 fr). One paused GSAP driver -> render(t); every visual is a pure function of the frame (no rAF, seeded grain).
- prep.py (run before every render) resolves upstream files and writes assets/ + assets/data.js; assets/manifest.json lists real vs placeholder (final: 0 placeholders, copy in render/manifest_final.json).
  Inputs: color/v002 plate + credits_graded_v002 (blur-5 glow underlay), layout/v001 cams/points/tracks/solve_stats/anchor, comp/v001 PNG sequences
  (final_2808, final_2160, plate_2160, cg_2160), lighting/v002 title_fg/bg, restore/v001 lineup_restored_2160_r470, color/v001 sf_logo_bone.
- Credits: native DOM list (credits.txt verbatim + 3 rows read from movie.mp4 67.40 above line 1), Inter Tight 500 ls 0.10em (matches source glyph widths);
  overlay diff: type within 1 px of row_track prediction, underlay +4 px (VFIX -0.125). Push = per-frame font-size (no CSS scale on text). His row Inter Tight 800,
  SVG brush plate (feTurbulence seed 7 + displacement 26, dry-brush mask) paints in f45-51, name turns Ink. Line-up r470 bottom-aligned, RGBA glows.
- TRACK: tracks.json drawn per frame (density step f82), 1 m grid via cams.json with SIMPLE_RADIAL (r2<1 guard). TILT/SOLVE: viewer camera from time, s51/s0 image
  planes via matrix3d homography, cloud with quarter-res bloom, 52 frustums; registration lands on cam s0 and pushes to the FINAL window of f169.
- FINAL: window x1.30 -> x1.55 (eIOS f169-220) on the Gaussian-smoothed monument centre; jolt f173; CONTACT s04 call-out + halo; LOCKED f208 on anchor front_left.
- HUD numbers read from solve_stats.json only. Editor cue fixes: f82 density, f302 studio line.
- Render: npx hyperframes@0.8.184 render -q delivery -f 25 --resolution portrait-4k -o render/vinay_v4_4K.mp4 . (9m35s, screenshot capture; log render/render.log).
