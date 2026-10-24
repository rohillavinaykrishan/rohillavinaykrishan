# sh010 mograph v001 - "THE SOLVE" main HyperFrames composition

- Project: this folder (`index.html`, HyperFrames 0.8.181), 2160x3840, 25 fps, 15.0 s (375 frames).
- Single GSAP driver tween; every visual is a pure function of t (`render(t)`), seek-safe. Freeze 11.96-12.28 holds every motion (embers, sparks, roll).
- Assets (copied in for a deterministic render): `assets/red_base_2160.png` (roto red_base.png downscaled from 2880x5120 to 2160x3840 -
  at full size Chrome only painted the top ~700 px of it, a hard band), `assets/sf_logo_alpha.png`, `assets/lineup.png` (roto v001),
  `assets/bg_plate_1080.mp4` (edit v003, freeze baked in), fonts in `assets/fonts` (Bebas Neue, Oswald 600, Inter variable, JetBrains Mono 500
  from Google Fonts), GSAP local in `assets/vendor`. `assets/ph/` = early placeholders, unused.
- Roll: verbatim from source/credits.txt; y0(t)=2700-2908*easeOutCubic((t-1)/(10.2-1)), row 19 right = VINAY KRISHAN ROHILLA lands at y=1920 on frame 255.
- Legibility: per-frame plate luma (signalstats, roll area) baked into PLATE_Y; plate opacity dips and scrim rises on the light-leak frames.
- "ROUND ONE!" call (frame 43): a small scale and warm-colour kick on the header.
- Render: `npx hyperframes render -q delivery -f 25 --video-frame-format png -o render/sh010_mograph_4K.mp4` (log in render/render.log).
- Check: 0 lint errors. Remaining layout-audit "text_occluded" findings are false positives from masked or canvas layers.
