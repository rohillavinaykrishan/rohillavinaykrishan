# sh010 mograph v002 - "THE SOLVE" main HyperFrames composition

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

## v002 changes (producer/creative review of v001)
- Background visibility: plate opacity 0.82 / 0.80 / 0.74 / 0.68, slam 0.95 -> 0.62; red base brightness x1.45. Replaced the frame-wide
  radial scrim with #scrimBand: a feathered horizontal band (~40-42% black, x 180-1980, lighter in the column gutter, vertical feather)
  only behind the roll; the top/bottom gradient is now lighter. Light-leak protection kept (plate dips up to 60% on the bright frames).
- Hero: after the lock (1.28x in place) the name glides 10.6-11.4 to the exact frame centre and scales up to 1780 px wide (Inter 700, gold),
  with a warm radial halo plus a soft orange glow. The brackets and the TRK_07 SOLVED label (38 px) come with it. Other names drop to 0.15 opacity
  with ~5.5 px blur. Held through the freeze.
- Slam morph (frame 307+): the big name stretches toward the title block while the "VINAY KRISHAN / ROHILLA" block starts squashed to the name's
  box and expands to full size (7-frame expo), crossfading over 2 frames under the gold flash.
