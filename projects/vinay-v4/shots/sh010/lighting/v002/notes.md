# sh010 lighting v002 (director notes 16 + 17). v001 kept untouched (old design).

## Shot CG (note 17) - scripts/shot_scene.py, scripts/monument.py
- Opens layout/v001/solve_cam.blend (camera keys s0-s51, GROUND shadow catcher, MONUMENT_ANCHOR x 2.0 y 20.75 rz -12).
  Placeholders replaced by the asset: Unbounded 900 VINAY/KRISHAN/ROHILLA, space_line 0.64 (lines touch), 7.24 m wide,
  3.75 m top, depth 0.30, bevel 0.035 (res 3), mesh; plinth 7.8x1.0x0.24 (bevel 1.2 cm). Bone plaster #E9E1D3 rough 0.55,
  sand-dust gradient (#CDB08A, rough 0.9) on the lower 15 cm of plinth and letters, noise bump 0.05.
- Fall: layout keys z = 5(1-(i/4)^2) s0-s4, set LINEAR (landing on s4 = f173).
- Sun measured from the fighters' real shadows on s25 (3 shadow lines unprojected to the ground through cams.json):
  shadows run toward world az -160 deg -> sun position az +20 deg (from +Y toward +X), elevation 35 deg. Energy 6.5,
  angle 1.5 deg, colour (1.0,0.95,0.86). World 0.30 warm-neutral + a hazy halo toward the sun (pow3 x 0.9) for edge wrap.
  Front faces measure ~52% of the plate's sunlit sand (linear luma), rims/bevels to ~100%.
- Render: pinhole with 1.16 overscan (3257x1364, sensor 41.76 mm, lens 28.09 = layout distort.py default), 16 spp,
  adaptive 0.03, OIDN, motion blur shutter 0.5, film transparent. Per-frame render BORDER around the monument + its
  shadow + motion-blur margin (borders.jsonl); fix_shadow.py sets the Shadow Catcher pass to 1 outside the border.
- Outputs (frame numbers = s index 0-51 = layout/cams.json "frame"; plate file = s+1):
  cg/cg.%04d.png (RGBA 16-bit, Standard view, straight alpha, monument only - NO shadow in alpha),
  shadow/shadow.%04d.png (16-bit, linear multiplier: 1 = no shadow; RGB), mist/mist.%04d.png,
  exr/cg.%04d.exr (multilayer, linear: Combined, Shadow Catcher, Mist, CryptoObject; shadow catcher only valid in border).
  All need layout/v001/distort.py --width 2808 --overscan 1.16.
- Contact shadow: catcher minimum ~0.33-0.40 (density 0.6-0.67) at render; the comp's density gain reaches the 0.75 Umber target.
- Proxy check: proxy_shot/check_v3.png (+ _zoom): s0/s25/s51 over the plate; shadow direction matches the real shadows.

## Title (note 16) - scripts/title_scene.py
- Camera 0.35 m, lens 22 mm (36 mm sensor), looks up; letters 152-2010 px (86%, centred), top ~1290, plinth base ~2170,
  horizon ~2140 (top at y 900 is not reachable with the 1.93:1 monument at 88% width without extreme distortion).
- Key: sun behind, el 12 deg, 15 deg right (energy 9, warm) -> hot rims + light shafts through the letter gaps toward camera.
  Front fill: 7 m disk area light #F2EBDF front-left (850 W, linked to the monument only) -> faces 70-79% display.
  Marker Pink kicker: 0.9 m disk, left-rear (so the pink edge lands on the letters' LEFT sides as asked), 900 W, ~2% px.
  Sky (camera rays): Ink -> Umber -> hot sand horizon + sun disc/halo; fill world 0.10 neutral. Bone rough 0.42, coat 0.1.
- Comp in Blender: Fog Glow (thr 0.9, size 0.8, strength 0.6) + Streaks (thr 4, 4%). OIDN albedo+normal.
  fg alpha = max(alpha, luma(glow)) (premultiplied) so the rim bloom survives over the bg.
- title_fg.png (RGBA: monument + plinth + soft contact) and title_bg.png (sky, sun, ground, shafts, long shadows),
  2160x3840, 64 spp. Proxies: title/t01-t03*.png (t03 approved look; t03_sheet = comp / bg / fg-over-white / fg-over-black).

## Render times (shared 4-core CPU, 2 heavy jobs in parallel)
- Shot: 52 frames 3257x1364, 16 spp, 05:37:48-06:14:54 = 37 min (sum of per-frame 2206 s, 25-110 s/frame; s0-s4 fall
  frames are the slowest, larger border). QC: 52/52 cg/shadow/mist/exr, no empty frames, correct size, shadow = 1 at edges.
- Title: title_bg 15.5 min, title_fg 20.8 min (2160x3840, 64 spp, adaptive 0.02, OIDN albedo+normal).
- Check images: proxy_shot/final_check_s4_25_51.png (final frames distorted + over the plate), title/title_comp_check_4k.png.
