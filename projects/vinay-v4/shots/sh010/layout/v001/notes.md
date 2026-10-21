# sh010 layout v001 - matchmove (beach, trailer src frames 2982-3033)

## Plate
- `plate/plate.0001-0052.png` 1280x536: `select='between(n,2982,3033)',crop=1280:536:0:92`, `-fps_mode passthrough`.
  Pixel-identical to `edit/v001/plate/` (max abs diff 0 on all 52). Numbering matches the editor: plate.0001 = s0.
- In all JSONs `frame` = s index 0-51 = Blender scene frame; `plate_file` = editor file name.

## Solve (COLMAP, scripts/solve.sh + scripts/map_try.sh)
- feature_extractor SIMPLE_RADIAL single camera, 8000 features, CPU; exhaustive_matcher (7 min under load 16).
- Treatment 9.2 relaxed mapper options as written: FAILED (auto init pair s36/s38 is near-degenerate,
  BA pushed f to 1596 px / k1 -0.85, 2 images registered).
- Fix (model `colmap/sparse_p_10_25/0`): same relaxed options + lens prior in a copy of the DB
  (`database_prior.db`: f 999.16 px, k1 -0.1966 = director's 960 px solve scaled, prior_focal_length=1)
  + forced init pair s10/s25 (`--Mapper.init_image_id1 11 --Mapper.init_image_id2 26`). f and k1 refined freely by BA.
- Result: 52/52 registered, 4,817 points, 34,118 observations, mean reproj 0.660 px (COLMAP definition;
  0.743 px per observation, median 0.567), f 998.91 px @1280 (28.09 mm on 36 mm, hFOV 65.3), k1 -0.1975, pp fixed centre.
  Gate (52/52, <=0.8 px, f 900-1100) PASSED.
- Weak frames: s44-s51 (end whip, heavy motion blur): 48-293 tracks, 1.3-1.5 px.

## World (scripts/process.py)
- Z up, ground z=0, origin on the ground under camera s26, +Y = s26 forward. (Treatment 9.1 "s18" is the director's
  cm3 image index 18 = image 0019 = plate s26, the lookdev frame, verified by image matching.)
- Ground: RANSAC on points below 62% of the frame on s26, thr 0.15 units at the director's scale (scaled here), LSQ refined:
  1,733 ground points. Scale: mean camera height 1.0 m (treatment convention). Camera travel 4.21 m, rotation 39.2 deg.
- SCALE FLAG: with that scale the fighters measure 3.9-4.3 m (s15 woman 4.27 m, s25 man crouched 3.37 m), so the true
  camera height is about 0.45 m (true metres = units x 0.45). Kept the 1.0 m convention so the asset sizes and lookdev values
  stay valid; for true metres rerun `CAM_H=0.45 vfx-python scripts/process.py <model>` and rebuild the blend.
- Projection valid only for r2 < 1 (SIMPLE_RADIAL folds back past r = 1.30); clip before projecting long 3D lines.

## Monument placement (scripts/place_search.py, scripts/build_blend.py)
- Lookdev values x 1.5, y 12.5, rz -12 FAIL: base below frame bottom on s2-s11, off the right edge of the plate on s48-s51
  (x1 1403 > 1280), top 4% on s51. The 39 deg pan + tilt leaves no room for a 7.8 m plinth at 12.5 m.
- Chosen: x 2.0, y 20.75, rz -12 (closest passing placement, same rotation; still on open sand, vegetation line is at ~43 units).
  All 52 frames: inside the FINAL x1.30 window (crop_cx = Gaussian sigma 6 of the centre x, clamped 493-787, +-492.3 px),
  top 26.6-55.7% below the frame top, min margin 6 px (s51 right edge). Fighters pass in front on s0/s25/s51.
  On-screen size at plate res: 365-409 px wide, 188-238 px tall.
- Lock check: median residual of sand tracks within 6 m of the anchor = 0.2-0.6 px on s0-s43, 0.9-1.8 px on s44-s51.

## Lens (distort.py)
- Required overscan for k1 -0.1975 is 1.142, so the treatment's 6% overscan is NOT enough (5% of pixels at the corners and
  edges come out transparent). Render at >= 1.15: e.g. 2808x1176 -> 3257x1364 with sensor_width 36*3257/2808 = 41.756,
  lens unchanged 28.09 mm (about +20% pixels vs 1.06). distort.py defaults to 1.16.
- Verified: synthetic dot grid 0.03 px mean / 0.07 px max error; Cycles render from solve_cam.blend -> distort.py matches
  anchor.json bounds within 1 px (review/blend_distort_check_v001.png).

## Files
cams.json, points.json, tracks.json, solve_stats.json, anchor.json, ground_plane.json, solve_cam.blend, distort.py,
review/solve_v001.png, review/blend_distort_check_v001.png, scripts/*.
solve_cam.blend: SOLVE_CAM (52 keys, frames 0-51, 23.976 fps, plate as camera background), GROUND (80 m shadow catcher),
MONUMENT_ANCHOR (empty at rest) > MONUMENT_PLACEHOLDER (fall keys z = 5(1-(i/4)^2) on frames 0-4) > NAME_PLACEHOLDER
(Unbounded 900, space_line 0.70, 7.2 m wide, 3.99 m top) + PLINTH_PLACEHOLDER (7.8 x 1.0 x 0.24), SUN (lookdev values).
