# Treatment v4: "GROUND TRUTH"
VINAY KRISHAN ROHILLA · Sr. Matchmove Artist · DNEG · Street Fighter
15.0 s · 2160x3840 · 25 fps · 375 frames · ONE final output (+ <16 MB share copy)

Director data (inputs for departments, not reports): `shots/sh010/director/v001/`
- `cues.json`: **the source of truth for timing**: music window, every hit as a frame, plate source frames, act boundaries, palette, fonts
- `bed_112.10-127.10.wav` (reference bed), `mood_bed_112.10-127.10.json` (song_mood), `cand_110.json`, `cand_70.json` (Whisper re-checks of the candidate windows)
- `overview_0.png`, `overview_84.png` (the whole trailer at 1 fps), `cand_*.png`, `cand_strips*.png` (the candidate shots)
- `cm3_beach/` (the **COLMAP solve that worked**: database, `sparse_relax/0` TXT model), `cm4_beach/` (same shot at 640 px), `cm2_*`, `cm3_*` (the candidates that failed, kept as evidence)
- `ground_plane_beach.json` (fitted sand plane and metric scale), `solve_beach_reproj.png` (solved 3D points reprojected through the solved cameras), `layout_test_beach.png` (a test billboard and ground grid locked through the shot)
- `lookdev/comp2.png` (**proof of concept**: a Cycles-rendered 3D name on the real plate through the solved camera, frames 1 and 19), `lookdev/title_proxy3.png` (title monument proxy), `lookdev/*.blend` (both lookdev scenes), `lookdev/grade_test.png`
- `fonts/` (Unbounded, Inter Tight and JetBrains Mono TTFs, fetched from the Google Fonts CSS API)
- `credits_69.png`, `credits_scroll.png` (his row in the real crew-thanks roll)
- `director_v4_board.png` (all of the above on one board)

---

## 1. Big idea and logline
His name normally lives at the end of the film, in white type, in a roll nobody stops. A matchmove artist is the person who makes CG believe it was really there on the day. So we use his own craft to **move his name out of the credits and into the movie**: we take a real Street Fighter trailer shot, solve its camera for real (COLMAP, real numbers), and stand his name in the sand as a lit 3D monument. The fighters fight in front of it, its shadows fall on the beach, and it is locked to a handheld camera that whips through 39 degrees. Then we show the work the way every VFX reel does: plate, track, solve, CG, final. It ends on the name as a monument of its own.

**Logline:** *The name from the end credits walks into the movie and stands its ground, placed there by the craft of the man it belongs to.*

Title of the piece: **GROUND TRUTH**. In matchmove the ground plane is the reference everything else is solved to. His name literally stands on the solved ground, and every number on screen is the true number from our solve.

### Why this is better than PARALLAX, and different from both
| | v3 THE SOLVE | PARALLAX | **v4 GROUND TRUTH** |
|---|---|---|---|
| Craft shown | 2D tracker boxes on a text roll (a metaphor) | a fake 3D camera through floating names (a metaphor) | **a real camera solve of a real movie shot, with real CG integrated in it** (the actual job) |
| Where the name lives | flat text over a dim plate | floating DOM text in a CSS 3D space | **a physical, lit, shadow-casting 3D object inside the film's world, with fighters occluding it** |
| Numbers on screen | none | an illustrative ERR count-down | **true solve data**: cameras registered, points, reprojection error, focal, k1 |
| Structure | one long roll | one long fly-through | **VFX-reel grammar**: credits → TRACK → SOLVE → FINAL → 4-band BREAKDOWN → title |
| Light / world | night, fire, red-gold | night, silver B&W, lime | **daylight**: sun-bleached sand, sage dunes, bone white, ONE Marker Pink accent |
| Plate | 1 trailer window as dim BG | soft 9:16 crops at 28-70% | **the 2.39 plate at full width (1.69x, sharp enough)**, never a 7x vertical crop |
| Title | Bebas over line-up art | Bodoni ivory on black + silver logo | **the name as a 3D monument in low sun** (native 4K Cycles), with Unbounded/Inter Tight type and a bone logo. A light card, where both earlier pieces end dark |
| Music | 61-76 ("ROUND ONE!") | 141-156 | **112.10-127.10**, never used before |

## 2. What the material says

### Music: trailer 112.10-127.10 s (dialogue-free, verified)
- The whole-trailer Whisper pass showed a word gap from 112.91 to 126.27, but it also logged stray words. I re-transcribed **110-132 s on its own** (`cand_110.json`): "Oops you dropped something" ends at **112.03**, and the next word is "I (made a promise)" at **127.18**. Nothing in between. The window 112.10-127.10 therefore starts 70 ms after the last word and ends 80 ms before the next one. Sound listens once to 112.10-112.40 for a consonant tail (the 3-frame fade-in covers it) and to 124.4-126.5, where any fighter grunt is part of the mix and acceptable.
- song_mood: 172 BPM (double time; the felt pulse is about 86), D minor, energy high with one hole. It suggests `punjabi-night` (teal shadows). **Rejected.** Teal is exactly the "accidental blue" the client hates, and our hero plate is daylight. Grade: section 5.
- Shape (40 ms RMS grid, `cues.json`):
  - f0-5: low (-30 dB), rises at **f6** (112.34)
  - f6-136: percussive drive, hits at **f69** (114.86), f81, **f113**, f121
  - f137-142: first dip (117.58, -30 dB), pickup at f141
  - **f159-165: true near-silence** (118.46-118.70, -34 dB)
  - **f173: HERO, the re-entry** (119.02). The level jumps by +21 dB in one 40 ms bin, the most violent transient in the window. **The monument lands here.**
  - f208 (120.42), f251 (122.14): drive hits
  - **f275: TITLE, the loudest sustained hit** (123.10, -10.9 dB RMS)
  - f291 (123.74), f304 (124.26): two more big hits, used for the title's type lines
  - 14.40-15.00: fade (the bed ends before "I" at 127.18)

### Emotion (no lyrics, so the arc comes from the purpose)
Anonymity → craft → arrival → authority. It starts as one row among hundreds in a roll. Then we watch the hands-on work (the tracks, the solve), then the name **arrives** inside the movie with a physical impact. Then the work is shown openly (the breakdown is a matchmove artist's proof). Finally the name **stands alone**: a monument in late sun, with no UI left. This piece is about **pride earned by precision**, warmer and more confident than PARALLAX's cool control, and more grounded than v3's fire.

## 3. Feasibility work (done, with evidence)

### 3.1 Candidate shots (active picture `crop=1280:536:0:92`; I extracted and looked at all of them)
| Candidate | src (s) | Surface for the name | COLMAP result | Verdict |
|---|---|---|---|---|
| **A. Beach fight** | **124.374-126.543** (52 fr) | wide sand floor, dune behind, hard sun | **37/37 registered, 3,524 pts, 0.60 px** (960 px) · **37/37, 2,022 pts, 0.603 px** (640x268) | **CHOSEN** |
| B. Arena light-shafts leap | 135.68-137.26 | far wall / banner in light shafts | 2-4 registered, 0 pts; pairs flagged PLANAR_OR_PANORAMIC | pure tilt (nodal), no parallax |
| C. Market street | 27.15-28.57 | brick wall, overhead banner | 3 registered; pairs flagged WATERMARK/static | camera nearly locked off |
| D. Penthouse push-in | 56.89-58.93 | floor, window wall | 43/46 registered but f = 26,435 px (degenerate) | too little translation, rejected |
| E. Dojo slats | 59.56-61.98 | slat wall | 35/46, 500 pts, 1.12 px | solvable but dark, few points, a face close-up |
| F. Skyscraper banner | 35.45-36.70 | giant banner on a tower | 9/31, f = 11,677 px | telephoto, near-nodal |
| others | 0.0-1.5, 78-82, 103-105, 112.6, 140.7, 8.2 | | 2-6 registered | rejected |

**Why A wins:** it is the only shot with real camera translation that COLMAP solves completely and cleanly. The camera moves **3.8 m** (baseline/depth 0.29) and rotates **38.6 degrees** in 2.17 s, which is real handheld parallax. It has a huge clean ground plane (1,193 RANSAC inliers on the sand), a hard sun with readable shadows to match, and **fighters crossing in front**, so occlusion proves the integration. It is daylight, unlike anything in v3 or PARALLAX, and none of v3's (37-52, 94, 119, 124-126 as a *dim BG*) or PARALLAX's shots is reused as a hero plate. (v3 had 124-126 as a 2D background under the roll. Here it becomes a solved CG shot, a completely different use.)

**COLMAP lesson for layout (important):** the stock `automatic_reconstructor` failed on every candidate ("No good initial image pair"). Two causes, both fixed:
1. `init_min_tri_angle` 16 is far too strict for a 2 s shot. Use 0.5 (plus `filter_min_tri_angle 0.3`, `tri_min_angle 0.3`, `local_ba_min_tri_angle 1`).
2. After the first 2-view bundle adjustment, the camera fails COLMAP's "bogus params" check, so every later image says "Could not register" in 0.2 ms. Use `--Mapper.max_focal_length_ratio 100 --Mapper.min_focal_length_ratio 0.05 --Mapper.max_extra_param 100`.
Working recipe: `director/v001/scripts/cm3.sh` and `scripts/map.sh`, reproduced in section 9.2. The result is SIMPLE_RADIAL, **f = 749.4 px at 960 wide (hFOV 65.3 degrees), k1 = -0.197**, principal point fixed at the centre.

**Proof of integration:** `lookdev/comp2.png`. Blender 5.2 builds the camera straight from `images.txt` (world-to-camera quaternion → `R^T·diag(1,-1,-1)`), the ground plane comes from `ground_plane_beach.json`, and the text is Unbounded 900 on a shadow catcher. It renders **24-31 s per frame at 2160x904, 16 spp + denoise**. The name holds its place on the sand between frames 1 and 19 while the camera moves and rotates. Still missing, by design: occlusion (roto), lens distortion, motion blur, final lighting and the grade.

**Fallback (if the 52-frame solve fails):** keep the 37-frame model and add the missing frames with `colmap image_registrator`. If that fails too, do a 2D planar track of the sand (OpenCV homography on the RANSAC ground features → per-frame corner pin) and lay the name *flat on the sand* as painted/pressed lettering (an honest "2D track" version). depth.py is not needed.

## 4. Visual world
- **One real world:** a sunlit beach fight from the film: pale sand, sage dunes, white sky, one red suit. It is shown at its true 2.39 aspect at full width (2160x904, a 1.69x lanczos scale) so the plate is clean. Above and below the band, the frame is filled by an **ambient bleed**: the same plate scaled to fill the frame, `gblur=60`, at 22%, under an Ink vignette. The phone screen is never empty black, and the band stays the sharp focus.
- **The object:** the name as a stacked monument, `VINAY / KRISHAN / ROHILLA`, in Unbounded 900, extruded 0.30 m, bevel 0.02 m, standing on a 0.24 m plinth slab. The lines touch (space_line about 0.70) so it reads as one solid sculpture, not floating text. Total about 7.2 m wide and 4.2 m tall, placed about 12.5 m from the camera behind the fighters (layout decides the final placement, section 9.2). The material is **bone plaster**: base `#E9E1D3` (linear about 0.80/0.74/0.64), roughness 0.55, sand-coloured dust darkening in the bottom 15 cm (a gradient mask). It is the classic integration object: white, so the light on it proves the match.
- **Graphics language:** VFX-reel restraint. Hairlines, small mono labels, act numbers `01 TRACK · 02 SOLVE · 03 FINAL · 04 BREAKDOWN`. No HUD clutter, no scanlines, no glitch.
- References (by style only): VFX studio breakdown reels (stacked passes, plate/CG wipes), brutalist land-art lettering in a desert, daylight A24-style poster minimalism.

## 5. Colour direction: "SUN-BLEACHED + MARKER PINK"
Grade family: **sun-bleached daylight.** Warm-neutral, slightly lifted blacks (Ink, not pure black), creamy highlight roll-off, greens pulled to sage, sky kept cream-white. **One accent, Marker Pink**, used only in graphics (track markers, the lock tag, one rule on the title). Pink is the complement of the sage dunes (designed contrast), it is a real tracking-marker colour, it is not red or gold (v3), not lime (PARALLAX), and it is not blue.

| Role | Hex | Use |
|---|---|---|
| Ink | `#12100D` | base, lifted blacks, background of all UI acts |
| Umber | `#3A2E24` | shadows, title sky top, vignette |
| Sand | `#CDB08A` | the plate's sand, title ground, secondary type |
| Bone | `#F2EBDF` | the monument, title type, the logo, HUD text |
| Sage | `#7D875C` | the plate's dunes, ground-grid hairlines (15-25%) |
| **Marker Pink** | `#FF2E88` | track "+" markers, lock tag, solve frustum of the current frame, the title rule. **≤ 3% of pixels** |
| Pink glow | `rgba(255,46,136,.35)` | 1-frame halo at the landing only |

**Plate grade (colorist):** keep the exposure. Mean Y within ±5% of the source (my quick test `lookdev/grade_test.png` went too dark and sepia; do not do that). Direction: saturation 0.88; greens hue-shifted toward olive/sage; highlights roll off to `#F2EBDF`, not to white; blacks lift to `#12100D`; sky stays cream. Light grain, `noise=alls=5:allf=t`. **QC:** for every frame, mean B ≤ mean G ≤ mean R and VAVG ≥ 128. The source frame already measures R 143 / G 127 / B 107, so it is warm and nothing needs to be fought; just never cool it.
**Credits grade (the red roll):** a duotone into our palette: `hue=s=0,curves=master='0/0 0.45/0.18 1/1'`, then map black → Ink and white → Bone (`curves=r='0/0.071 1/0.949':g='0/0.063 1/0.922':b='0/0.051 1/0.875'`). The red becomes a deep warm Umber, the names become Bone, and the v3 red disappears. Fade the bottom 32% of the roll frame (line-up art + DNEG watermark) to Ink.
**Logo:** `assets_prev/sf_logo_alpha.png` → greyscale → mapped Umber→Bone (the brush texture stays), alpha kept, so it is **bone**, not colour (v3) or chrome (PARALLAX).

## 6. Shots
| # | Frames | Source | Crop / scale / centre | Notes |
|---|---|---|---|---|
| C1 credits | f0-68 | `movie.mp4` 67.40 → 70.16, 1.0x (25 fps native) | 720x1280 → 2160x3840 full-bleed; 2D push 1.00 → 1.22 centred on his row (src x 465, y ≈ 607 at 69.20 s; the editor measures exactly) | His row "VAMSI KRISHNA EADALA \| **VINAY KRISHAN ROHILLA**" passes the frame centre around 69.0-69.2 s |
| P1 TRACK pass | f69-120 | trailer **src frames 2982-3033** (124.376-126.502), `select='between(n,2982,3033)'` | full active width 1280x536 → band 2160x904, centre y 1920 | 1:1 frame conform (no interpolation) |
| P1 hold | f121-136 | src frame 3033 | band → tilts into 3D (the image plane of camera 52) | |
| SOLVE | f137-168 | pure graphics (points.json, cams.json); s0 image plane from f159 | full-frame 3D viewport | |
| P1 FINAL pass | f169-220 | src frames 2982-3033 (+ CG + roto) | band ×1.30 → 2808x1176, cropped to 2160 wide; **CX follows the monument anchor** (src px, clamp 493-787; default 640 → 700) | monument falls s0-s4, contact on **f173** |
| P1 BREAKDOWN | f221-272 | src frames 2982-3033, four versions | 4 stacked bands 2160x904 at y 64 / 1000 / 1936 / 2872 | PLATE · TRACK+SOLVE · CG · FINAL |
| TITLE | f275-374 | CG stills (native 4K) | full frame | |

## 7. Second by second
| t (frame) | Picture | Music |
|---|---|---|
| 0.00 (0) | **The real crew roll**, in duotone (Ink/Bone), both columns legible. His row is already Bone 100%; all other rows 55%. A pink 4-corner bracket sits around VINAY KRISHAN ROHILLA, label `TRK 01` (JetBrains Mono 30 px). Slow push begins. Top-left HUD: `SOURCE · CREW THANKS ROLL` | bed in (3-frame fade) |
| 0.24 (6) | the bracket tightens (an 8-frame ease) | first rise |
| 1.0-2.4 | the push continues; the other rows fade to 35%; HUD: `NAME · VINAY KRISHAN ROHILLA` | drive |
| 2.40-2.72 (60-68) | **the bracket's 4 corners fly out** to become the 4 corners of a 2160x904 band at the frame centre; the roll darkens to Ink inside it | |
| **2.76 (69)** | **CUT INTO THE MOVIE**: the beach plate fills the band (P1 s0). Act label `01  TRACK` (Inter Tight 600, 54 px, letter-spacing 0.3em, Bone 70%, x 96, y 1380). Ambient bleed above and below | drive hit |
| 2.76-4.8 | **real tracks appear**: the 2D observations from the solve (points2D with a valid point3D id) are drawn as 12 px pink "+" with 4-frame trails, opacity ramping 0 → 0.9 over f69-95 and density stepping up on f81. Under the band: `TRACKS 0612` (the live count per frame from images.txt) | hits f81 |
| 4.52 (113) | **the solved ground grid** draws itself across the sand: a 1 m grid in Sage hairlines, projected through each frame's real camera, so it sticks to the beach as the camera whips | hit |
| 4.84-5.44 (121-136) | band freezes on s51; it desaturates 30% and **tilts back into 3D**: it becomes the image plane of camera 52 floating in the dark | hit f121 |
| **5.48 (137)** | `02  SOLVE`. **The 3D viewport fills the vertical frame** (native 4K canvas): the point cloud (each point in its true plate colour, 3 px), the ground grid, and the **52 camera frustums registering one by one** along the handheld path (Bone hairlines, current one pink). HUD bottom: `CAMERAS 52/52 · POINTS 3,5xx · MEAN REPROJ 0.60 px · f 34.6 mm eq · k1 −0.197` (true values from `solve_stats.json`, never typed by hand) | dip |
| 5.6-6.3 | the viewport orbits about 40 degrees around the cloud: the beach as a sculpture of coloured dots, the fighters as smeared streaks (honest: moving objects don't solve) | pickup f141 |
| **6.36-6.60 (159-165)** | **REGISTRATION** (in the silence): the virtual camera glides into camera 1's exact pose; the s0 plate fades in on its image plane; **every dot lands on its pixel**. A pink wireframe of the monument appears on the grid (f165) | **near-silence** |
| 6.76 (169) | `03  FINAL`. Band ×1.30. Rendered frame s0: the monument starts 5 m above its mark (falling under gravity) | |
| **6.92 (173)** | **THE LANDING**: the monument hits the sand on the re-entry. Its contact shadow snaps sharp, a 3-frame comp jolt (8 px vertical, decaying), a 1-frame pink halo on the "+" at its base. The fighters keep fighting **in front of it** (roto occlusion), its shadow lies on the real sand, the handheld camera whips and the name stays locked | **HERO hit (+21 dB)** |
| 7.0-8.8 | the shot plays out; a pink tag `+ LOCKED` is pinned to the plinth's front-left corner (the 2D projection of the 3D anchor, so it moves with the solve) at f208. Under the band: `CG · CYCLES · SHADOW CATCHER · ROTO HOLDOUT` | hit f208 |
| **8.84 (221)** | `04  BREAKDOWN`: **four stacked bands fill the phone**, all playing s0-s51 in sync: PLATE / TRACK + SOLVE (pink tracks + grid + monument wireframe) / CG (the monument and its shadow over warm 18% grey `#6E665C`) / FINAL. The bands slide in from the right, staggered 3 frames (f221, 224, 227, 230). Labels top-left of each band, JetBrains Mono 600 28 px, Bone | drive |
| 10.04 (251) | the FINAL band's 2 px Bone border flashes 1 frame | hit |
| 10.92-11.0 (273-274) | the four bands fold toward the centre (2 frames, ease-in) | |
| **11.00 (275)** | **TITLE**: hard cut, with a 2-frame Bone flash at 50%. **The monument, alone**, native 4K: a low 3/4 angle, late sun, long shadows, a dusk gradient sky; it settles from scale 1.06 to 1.00 by f290 (as if it had just landed), then a slow push to 1.03 | **loudest hit** |
| 11.32 (283) | the SF logo (bone) fades in, 8 frames, y 330-790, 1100 px wide | |
| 11.64 (291) | the pink rule (420x6) draws left to right in 8 frames; `SR. MATCHMOVE ARTIST` rises 24 px and fades in | hit |
| 12.16 (304) | `STREET FIGHTER  ·  DNEG` | hit |
| 12.2-15.0 | poster hold with the push. **No fade to black**: the last frame is the poster (loops cleanly on Reels) | fade 14.40-15.00 |

## 8. Typography (Google Fonts; TTFs in `director/v001/fonts/`, CSS API reachable)
- **Unbounded 900**: the monument (Blender text) and nothing else. Wide, geometric, heavy; it extrudes beautifully and reads at thumb size.
- **Inter Tight 600**: role line, act labels. **Inter Tight 500**: studio line.
- **JetBrains Mono 400/600**: HUD, band labels, numbers.
- **Title card layout** (2160x3840; safe area x 160-2000, y 300-3000):
  - SF logo, bone, 1100 w, centred, y 330-790
  - monument render: letters span about 1840 px wide, the top of VINAY at y ≈ 1020, the plinth's base at y ≈ 2480, horizon at y ≈ 2330
  - pink rule 420x6, centred, y 2700
  - `SR. MATCHMOVE ARTIST`: Inter Tight 600, 96 px, letter-spacing 0.26em, Bone, centred, y 2830
  - `STREET FIGHTER  ·  DNEG`: Inter Tight 500, 64 px, letter-spacing 0.42em, Sand `#CDB08A`, y 2990
  - a bottom gradient, Ink 0% → 75% from y 2550 to 3840, so the type sits on dark ground
- Spelling (verbatim): `VINAY KRISHAN ROHILLA`, `SR. MATCHMOVE ARTIST`, `STREET FIGHTER`, `DNEG`. No years, no other roles, no invented shot codes. The only numbers shown are measured ones (solve stats, frame counts, trailer timecode).

## 9. The 3D plan

### 9.1 Coordinate system
`ground_plane_beach.json` gives the sand plane (normal, d) and a metric scale based on an **assumed mean camera height of 1.0 m** (the camera is low; layout may refine it from the fighters' height ≈ 1.75 m). World: Z up, ground z = 0, origin under camera s18, +Y = s18's forward direction projected on the ground. The lookdev scripts (`lookdev/cg2_0019.blend`, `director/v001/scripts/lookdev.py`) already implement the transform, and their output matches the plate.

### 9.2 Layout-artist (solve)
1. Extract **all 52 frames** at 1280x536 (`select='between(n,2982,3033)'`, `crop=1280:536:0:92`, `-q:v 1`).
2. COLMAP: `feature_extractor` (SIMPLE_RADIAL, single camera, `SiftExtraction.use_gpu 0`, max 8000 features) → `exhaustive_matcher` (`SiftMatching.use_gpu 0`) → `mapper` with **these options**: `--Mapper.init_min_tri_angle 0.5 --Mapper.filter_min_tri_angle 0.3 --Mapper.local_ba_min_tri_angle 1 --Mapper.tri_min_angle 0.3 --Mapper.init_min_num_inliers 30 --Mapper.abs_pose_min_num_inliers 15 --Mapper.ba_refine_principal_point 0 --Mapper.multiple_models 0 --Mapper.max_focal_length_ratio 100 --Mapper.min_focal_length_ratio 0.05 --Mapper.max_extra_param 100`. About 3-4 min. Gate: **52/52 registered, mean reprojection ≤ 0.8 px, f within ±10% of 1000 px at 1280** (749.4 × 1280/960 = 999). Otherwise use the fallback in section 3.
3. Re-fit the ground plane (RANSAC on points that project below 62% of the frame height, threshold 0.15 units). Write `cams.json` (per frame: K, k1, R, t in metres in the Z-up world), `points.json` (xyz + rgb, ground inliers flagged), `tracks.json` (per frame: the 2D points with a 3D id, for the TRACK overlay), `solve_stats.json`.
4. `solve_cam.blend`: an animated camera (52 keys, sensor_fit HORIZONTAL, lens = f/w·36), the ground plane, and a null `MONUMENT_ANCHOR`. **Monument placement:** start at x +1.5, y 12.5, rot Z −12 degrees (the lookdev values), then verify on s0 / s25 / s51 that (a) it stays fully inside the FINAL ×1.30 window, (b) the fighters pass in front of it, (c) its top stays at least 6% below the top of the frame. Export `anchor.json` (per-frame 2D projections of the plinth's 4 base corners and the monument's centre → the FINAL crop CX and the LOCKED tag).
5. **Lens:** write `distort.py`: render the CG with pinhole optics at 6% overscan and apply SIMPLE_RADIAL (u = f·x·(1+k1·r²)+cx, normalised coordinates) with `cv2.remap` to every RGBA frame. Verify it with a grid image overlaid on the plate.

### 9.3 Asset / lighting (Blender 5.2, Cycles CPU)
- Geometry: Unbounded 900 text `VINAY\nKRISHAN\nROHILLA`, align centre, space_line ≈ 0.70 (the lines must touch), extrude 0.30 m, bevel 0.02 m (res 3), converted to mesh; plinth 7.8 x 1.0 x 0.24 m. The bevels catch the sun, which is what sells the scale.
- Material: Principled, base `#E9E1D3`, roughness 0.55, plus a sand-dust gradient on the lower 15 cm (`#CDB08A`, roughness 0.9) and a subtle noise bump (0.05).
- **Shot lighting (match the plate):** the plate is **backlit**: the sun is in front of the camera, high-right, and the feet's shadows fall toward the lower-left of frame. Sun lamp: energy ≈ 4.5, angle 1.5 degrees, colour `(1.0, 0.95, 0.86)`, azimuth about 40 degrees right of the view axis, elevation about 35 degrees; layout/lighting align it so the monument's shadow is parallel to the fighters' real shadows on s19. World: warm-neutral `(0.80,0.76,0.70)`, strength 0.45-0.5 (sky fill). The front faces should sit at about 55-65% of the sunlit-sand luminance, with bright rims on the tops and right sides.
- **Shadow catcher:** an 80 m plane, `is_shadow_catcher`, film transparent. The fall animation: z = 5·(1−(i/4)²) for i = 0..4 (s0-s4), then z = 0.
- **Motion blur ON** (shutter 0.5; the plate's whips are heavily smeared, and the CG must smear the same way).
- **Render passes** (EXR multilayer or PNG RGBA): `Combined` (RGBA with the shadow in alpha), `Shadow catcher` (separate, for grading the shadow density), `Mist` (for a 3% haze match), `Cryptomatte object` (optional). The breakdown's CG band = Combined over `#6E665C`.
- **Resolution and samples:** **2808x1176** (+6% overscan → 2976x1248), **16 spp, adaptive threshold 0.03, OIDN denoise**. Measured: 24-31 s/frame at 2160x904/16 spp. Estimate **≈ 55-65 s/frame → 52 frames ≈ 50-55 min** in one heavy slot (4 threads). Proxy first: s0 / s25 / s51 at 1080x452, 8 spp (≈ 6 s each) for director approval.
- **Title monument (native 4K stills, not an animation):** a separate scene (`lookdev/title_proxy3.blend` is the starting point). Camera 34 mm-equivalent, low (0.55 m), 3/4 from front-left, monument fills about 85% of the width. **Sun front-left behind the camera, elevation ≈ 24 degrees** (the front faces lit, long shadows falling back-right), so the bone letters read against a **dusk gradient sky: Ink (top) → Umber → Sand glow at the horizon** (a world ColorRamp on the Generated Z axis, camera rays only; a separate constant fill for lighting). Sand ground with noise bump, a mist pass for distance haze. Render as **two layers at 2160x3840**: `title_fg` (monument + plinth + contact shadow, RGBA) and `title_bg` (sky + ground + long shadow), 64 spp + OIDN. Estimate ≈ 4-6 min each. These give the 2.5D push (fg 1.00→1.03, bg 1.00→1.012).

### 9.4 Roto (occlusion)
- `roto.py` with `--model u2net_human_seg --mode matte` on the 52 plate frames at 1280x536 (≈ 0.7 s/frame, ≈ 1 min). This is the holdout for **all people** (every fighter is closer than the monument).
- Check s25-s51 for the black helicopter body (left) and the rotor blade (top-left diagonal). If either crosses the monument in the final placement, use `sam_roto.py --point` on the blade (≈ 3.5 s/frame, 52 frames ≈ 3 min).
- Matte clean-up: a temporal median over 3 frames, erode 1 px, blur 1.5 px (motion-blurred edges), check over black and white. No flicker on the monument's edges.

### 9.5 Compositor (ffmpeg / Python, at the 2808x1176 FINAL resolution)
For each frame: graded plate (lanczos 2.19x) → CG (distorted, then **degraded to match**: gblur σ ≈ 1.0, chroma blur, grain matched to the plate `noise=alls=6:allf=t`, black level lifted to `#12100D`, 3% mist haze) → **holdout**: CG × (1 − person matte) → shadow: multiply the plate by the catcher shadow (density 0.65, colour Umber-tinted, not grey) → **light wrap**: the plate's sky bleeding 4% onto the monument's edges → a 3-frame jolt at f173 (applied in mograph, see below).
Outputs: `final_band_2808x1176.mov` (52 fr), `cg_band_2160x904.mov` (Combined over `#6E665C`), `plate_band_2160x904.mov`, `final_band_2160x904.mov` (for the stack). QC: check the shadow direction against the fighters' real shadows; no edge halo over black or white.

## 10. Sound plan: ONE real trailer bed, nothing synthetic
- `source/trailer.mp4` **112.10-127.10** (`atrim=112.10:127.10,asetpts=PTS-STARTPTS`), stereo 48 kHz, uninterrupted from frame 0 to 374. A 3-frame fade-in and a 0.6 s fade-out from 14.40 (the bed ends 80 ms before "I" at 127.18; make sure nothing of it leaks).
- **The picture is cut to the music; we add no sound to the picture.** The bed already carries the cut into the movie (f69), the hole (f159-165), the landing (f173), the title (f275) and the type hits (f291, f304).
- Creative move (different from v3's low-pass and PARALLAX's stereo narrowing): **none on the music. The silence is real.** The trailer's own near-silence at 118.46-118.70 is where the registration happens. Leave it untouched; the +21 dB re-entry is the landing.
- **Banned:** every synthetic sfx (whoosh, riser, impact, tick, shimmer, glitch, drone), any tracker "beeps", any sub reinforcement.
- Master: -14 LUFS integrated, ≤ -1 dBTP after AAC (`tools/vfx/bin/master_audio.sh`). QC: the 119.02 transient on f173 ±1 and the 123.10 transient on f275 ±1.

## 11. The Short / thumb-stop
The whole piece is the Short. **The thumb-stop is f173-272:** a lit 3D name slams into the sand of a real Street Fighter fight, the fighters keep fighting in front of it, and then the screen splits into four synchronized versions of the same shot (plate / track / CG / final). Nobody has seen a credit do that.
Frame 0 is already strong (a real credit roll with one name bracketed in pink), never black.
**Cover frame: t = 14.4** (the monument title card, full name and role). Alternative cover: f236 (the four-band stack).

## 12. Build plan (4 cores, about 2.5 h wall clock, heavy jobs ≤ 2)
| # | Dept | Task | Outputs (`shots/sh010/<dept>/v001/`) | Heavy? | Est. |
|---|---|---|---|---|---|
| 1 | **editor** | The 52 plate frames (1280x536 PNG, src 2982-3033), credits clip (movie 67.40-70.16, 69 fr), measure his row's y per frame, `cues.json` sanity check | `plate/plate.%04d.png`, `credits_src.mp4`, `row_track.json` | no | 15 min |
| 2 | **layout-artist** | full COLMAP solve (section 9.2), ground plane, `cams.json`/`points.json`/`tracks.json`/`anchor.json`/`solve_stats.json`, `solve_cam.blend`, `distort.py`, verification sheet (points + grid + monument box on s0/s25/s51) | as listed | yes (COLMAP, ~4 min) | 25 min |
| 3 | **roto** | rembg human matte (+ SAM 2 blade if needed) | `matte/matte.%04d.png`, `matte_check.png` | yes (short) | 10 min, in parallel with 2 |
| 4 | **colorist** | plate grade (`sunbleach.cube`), credits duotone, bone logo; chroma QC | `plate_graded/…`, `credits_graded.mp4`, `sf_logo_bone.png` | no | 20 min |
| 5 | **asset/lighting** | monument asset, shot lighting; **proxy s0/s25/s51 → director OK**; final 52-frame render (section 9.3), then the 2 title stills | `cg/cg.%04d.exr`, `title_fg.png`, `title_bg.png`, `.blend` files | **yes, ~55 min + ~12 min** | 15 min setup + renders |
| 6 | **compositor** | the FINAL comp, the band versions, the CG-over-grey band; edge/shadow QC | `final_band_2808.mov`, `plate_band.mov`, `cg_band.mov`, `final_band_2160.mov` | light | 25 min |
| 7 | **motion-graphics** (HyperFrames, 2160x3840, `data-fps=25`, `data-duration=15`) | all acts: credits push + bracket, the TRACK canvas overlay (from tracks.json, drawn per frame through cams.json), ground grid, the **SOLVE viewport** (canvas 2D pinhole projection of points.json + frustums, camera evaluated from time, no rAF), band layouts, the 4-band stack, the LOCKED tag, the f173 jolt, the title type + logo + 2.5D push, ambient bleed. **Proxy** (540x960) + snapshots at 0.3 / 2.6 / 3.5 / 4.7 / 5.9 / 6.5 / **6.92** / 7.8 / **9.4** / **11.0** / 14.4 s → director review → final 4K render, run alone | `vinay_v4_4k.mp4` (video only) | 4K render ~25-35 min | 60 min build |
| 8 | **sound** | bed cut, fades, master, onset QC | `bed_master.wav` | no | 10 min |
| 9 | **delivery** | mux, frame/fps/duration check, 4K master + <16 MB share copy | `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v4_4K.mp4`, `..._share.mp4` | light | 10 min |
| 10 | **director** | proxy lookdev approval, proxy cut review, final review | `review/director_v4_*.md` | no | 3 x 10 min |

**Critical path:** 1 → 2 → 5 (proxy, OK, render) → 6 → 7 (final 4K). Mograph builds the SOLVE viewport, TRACK overlay and title type as soon as layout delivers the JSONs (around T+25 min), using a placeholder band until the comp lands.
**Heavy-slot schedule:** T+5 COLMAP + rembg → T+40 Cycles shot render (slot A, ~55 min) → T+45 title stills (slot B, ~12 min) → T+100 comp (light) → T+115 mograph proxy → T+130 mograph 4K render (alone) → T+165 delivery.

**QC gates:** 2160x3840, 25 fps, 375 frames, 15.00 s. The landing on **f173**, the title on **f275**. The monument never slides relative to the sand (check the plinth corners against `anchor.json`: ≤ 1 px drift at plate res). Fighters always in front; the shadow direction matches the real shadows. All on-screen numbers equal `solve_stats.json`. Every type and graphics element is native 4K (DOM/canvas/Cycles), never an upscaled raster. No blue anywhere (B ≤ G ≤ R mean on the plate; pink appears only in graphics). Frame 0 is not black. The name is spelled exactly.

## 13. Risks and fallbacks
- **Solve fails on 52 frames:** use the 37-frame model + `image_registrator`; in the worst case, the 2D planar sand track → name pressed flat into the sand (section 3).
- **The monument looks like a "3D text template":** the fix is integration, not effects. Motion blur, matched grain/softness, a shadow tinted Umber, sand dust on the bottom, light wrap, correct backlight. The director checks the proxy on s0/s25/s51 before the long render.
- **Render over budget:** drop to 12 spp, or render at 2160x904 and limit the FINAL push to 1.15x.
- **The roto chatters on motion-blurred limbs:** the monument is behind the fighters at 12.5 m, so the edges cross it only briefly. Use the temporal median and a soft matte edge; SAM 2 on bad frames only.
- **The title looks grey or murky (proxy 1/2 did):** front-left sun at about 24 degrees + the dusk Ink→Umber sky (proxy 3 already reads). The lighting artist pushes the contrast of the faces against the sky; the director reviews a 540x960 proxy before the 4K stills.
- **The credits roll is 720 px wide (3x upscale):** it is only on screen for 2.7 s, in motion, as a duotone. Keep the push ≤ 1.22x. The pink bracket and HUD are native 4K.
