# Treatment v1 - "PARALLAX"
SUKANYA DILIP DHARIYA - Sr. Matchmove Artist - DNEG - Street Fighter
15.0 s, 2160x3840, 25 fps (375 frames), ONE final output.

Director data (inputs, not reports): `shots/sh010/director/v001/`
- `cues.json`: every cue as a frame number (music window, hits, plate shots with source in/out, speed, crop centre). This is the source of truth for the timing.
- `mood_bed_141-156.json`: song_mood output for the chosen music window
- `bed_141-156.wav`: the exact 15 s bed (reference only; sound re-cuts it from the source)
- `cand_139-159.json`, `cand_111-129.json`: Whisper re-checks of the two candidate windows
- `bg_candidates.png`, `bg_detail.png`, `crop_test_bw.png`, `crop_test_bw2.png`: shot selection and vertical crop tests (already in B&W)
- `sheet_140-158.png`, `sheet_150-154.png`: the picture under the music window
- `look_test.png`, `logo_silver_test.png`: a quick look test (silver logo over the B&W Chun-Li plate)

---

## 1. Big idea and logline
**Matchmove is the job of rebuilding a 3D camera from flat 2D pictures. This piece shows that job happening to the credit roll.**

The crew names float in a deep 3D volume, like an unsolved point cloud. The camera flies through them. Every name is a track point that is slightly wrong (wrong depth, plus a lime residual line showing how far it is from where it belongs). On the music's biggest hit the camera **solves**: the depth collapses, the residuals go to zero, the 3D field snaps flat into the real DNEG credit list, and the camera is centred on one name, SUKANYA DILIP DHARIYA. At the same frame the trailer itself cuts to Chun-Li, and a point cloud built from that very frame lands exactly on the picture. Then the trailer's own title stinger brings in the logo.

Logline: *A camera lost in a cloud of 89 names finds its solve, and the name at its centre is hers.*

### How it differs from Vinay's "THE SOLVE" (both will be seen side by side)
| | Vinay "THE SOLVE" | Sukanya "PARALLAX" |
|---|---|---|
| Space | flat 2D vertical roll | true 3D: perspective camera through a depth field of names, plus a 2.5D depth-parallax plate |
| Craft visual | 2D tracker boxes on names | 3D camera solve: lens-distortion grid that un-distorts, reprojection-residual vectors, point cloud registering onto the plate, solve-error readout |
| Palette | fire red / orange / gold, red poster base | silver-gelatin black and white, warm ivory, ONE electric accent (Solve Lime) |
| Logo | full-colour logo on screen for the whole piece | no logo until 13.0 s, then a **silver** logo on the trailer's own title stinger |
| Type | Bebas Neue / Oswald / Inter | Bodoni Moda (high-contrast serif) / Archivo Expanded / IBM Plex Mono |
| Music | 61-76 s, "ROUND ONE!", freeze on silence, slam on drop | 141-156 s: drive, a breath, the hit where the trailer cuts to Chun-Li, then the trailer's title stinger. Picture runs in sync with the trailer from 9.2 s |
| Shots | 37-52, 94, 119, 124-126, 136, 142-147 | 30.7-34.8, 108.6-109.3, 112.8, 117.9-118.5, 148.0-148.8, 150.2-154.0 (no overlap) |
| Ending | name card + colour line-up art | prestige film-title card, ivory serif on black, Chun-Li small in a window of light. No line-up art |
| Hero | trackers die, one locks, gold glow | the whole world snaps from 3D to flat in one frame |

## 2. What the material says
No lyrics. Like Vinay's, this is a credit for a person, so the emotional arc comes from the purpose: **craft, precision, quiet authority**. Hers is not "fire and pride" but **control**: the cool, exact person who makes the impossible shot line up. Chun-Li (the franchise's iconic female fighter, and the hero of our music window) is the visual partner: poised, precise, lethal. The respect for the team stays: every one of the 89 names in her section is on screen and legible at the solve.

### Music: trailer 141.00-156.00 s (dialogue-free, verified)
- Whisper whole-trailer pass: "To live is to fight" ends at 140.68 and the next real line is "You did that to your face" at 157.32. A stray word "You" at 146.98 had been logged. I re-transcribed **139-159 s** on its own (`cand_139-159.json`): "To live, is to fight." 139.21-140.69, then nothing until 157.2. I also ran **145-150 s** alone: 0 segments. The "You" is a hallucination on the 147.04 drum hit, so **141.00-156.00 has no dialogue**. (Sound must still listen once at 146.9-147.2 for a grunt. If there is one, it is a fighter's effort sound in the mix and is acceptable.)
- song_mood: 172 BPM (that is double time; the felt pulse is about 86 BPM), D major (confidence 0.5; it is really a modal, percussive action cue), "celebratory". **I reject the punjabi-gold grade suggestion.** It would put us back in Vinay's warm family, and the cue is percussive and precise rather than celebratory. The grade is chosen from the concept instead (see section 5).
- Shape (measured on a 40 ms RMS grid, plus a 10 ms transient check):
  - t 0.00-1.80: low intro, first hit at **t 0.49 (f12)** (141.49)
  - t 2.0-9.2: steady percussive drive. Hits at 2.80, 3.44, 4.60, **6.04 (147.04, loudest drum)**, 7.80, 8.20, 8.80
  - t 9.20-10.80: **the breath**. Level drops to -26 dB (150.2-151.8). The trailer shows a crouching fighter in smoke.
  - **t 10.84 (f271): HERO HIT.** The biggest transient (-9.1 dB peak at 151.84) after the breath. The trailer **cuts to Chun-Li on this exact frame** (scene cut measured at 151.818).
  - t 11.0-12.9: sustain, full energy
  - **t 13.01 (f325): TITLE HIT** (154.01). The trailer's own SF title stinger (flare cut at 153.945, logo at 154.07).
  - t 13.0-15.0: tail. Fade 14.3-15.0.
- The hero lands on the biggest hit, and the logo lands on the trailer's own logo hit. The music already holds the whole structure.

## 3. Arc
| Act | t (frames) | Emotion | Energy | Camera feel |
|---|---|---|---|---|
| I. LENS | 0.00-2.00 (0-49) | stillness, a woman alone in a dark warehouse; the lens is "raw" | low, first hit at 0.49 | locked off, slow push. A barrel-distorted lens grid straightens |
| II. FIELD | 2.00-9.20 (50-229) | scale: a whole crew, a whole film; we are inside the work | driving | forward dolly through the 3D name field, accelerating; arcs to an oblique 35 degree view |
| III. BREATH | 9.20-10.84 (230-270) | focus, held breath: the solve is converging | music dips | decelerating swing back to frontal; residuals shrink; point cloud rotates into register |
| IV. SOLVE | 10.84-13.00 (271-324) | recognition, quiet authority: *this is her shot* | peak, then sustain | **hard snap** to frontal, then a slow dolly back while her name comes forward in z |
| V. TITLE | 13.00-15.00 (325-374) | signature, prestige | stinger, then tail | near still. Push-in 1.000 to 1.025 |

## 4. Visual world
- **Silver-gelatin film noir in an industrial space**: the trailer's warehouse/dojo shots with hard window light, smoke and silhouettes, all in black and white. They become one world (the source has blue, red and green scenes; B&W unifies them and kills every colour-cast problem).
- Premium references by **style**: prestige-drama main titles (ivory serif on black, generous negative space), photogrammetry and point-cloud visualisation, camera-tracking software viewports drawn with editorial restraint (hairlines, not HUD clutter).
- Layer stack (bottom to top), always continuous with no slideshow cuts:
  1. Ink base `#070707`
  2. **Plate**: B&W trailer shots, 1080x1920, scaled to 4K under the type, with animated opacity (40-70%)
  3. **Depth fog**: a radial dark gradient that makes far names sink into black
  4. **Canvas layer** (one 2160x3840 `<canvas>`): lens grid, point cloud, lime track markers and residual lines
  5. **DOM name field** (89 names as real HTML text, positioned by the same JS camera, so it is vector-sharp at 4K)
  6. Title card, logo, HUD readouts
  7. Film grain (very light; the grain is baked into the plate, plus a 2% animated grain over the type so the type sits in the same world)
- **One camera, one projection.** A single JS pinhole camera (position, yaw, pitch, roll, focal length) is evaluated per frame from HyperFrames time (`hf-seek` / the timeline). The same `project(x,y,z)` drives the canvas points and the DOM names (left, top, scale, blur from |z - focusZ|). That guarantees true, consistent parallax. No WebGL is required (fast and deterministic on CPU). Three.js `Points` is an allowed alternative for the point cloud only, if mograph prefers.

## 5. Colour direction: "SILVER and LIME"
Grade family: **silver-gelatin B&W with a warm-paper ivory top end, plus ONE electric accent used only in graphics.**

Why: (1) It is the visual opposite of Vinay's fire, so side by side they read as a designed pair (fire / silver). (2) Matchmove lives in grey: plates are judged in luminance, and tracking UIs are monochrome viewports with coloured markers. (3) The trailer's blue/neon scenes become rich silver, so **no blue cast is possible**: the plate has zero chroma by construction, and the highlights lean warm ivory, never cold. (4) The accent, **Solve Lime**, is the colour every tracking app uses for "this point is locked". It is the colour of a solved track, it is never blue, and it is used on 3% of the pixels or less.

| Role | Hex | Use |
|---|---|---|
| Ink (deepest black) | `#070707` | base, crushed shadows |
| Carbon | `#16171A` | fog, the darkest plate mids |
| Graphite | `#3A3B3E` | far names, grid at rest |
| Silver | `#A9A9A6` | studio line, HUD text, the logo's mid-tones |
| Pearl | `#D9D5CC` | field names |
| Ivory (paper white) | `#F4EFE6` | her name, the title, plate highlights |
| **Solve Lime (the ONLY accent)** | `#C6FF3D` | track "+" markers, residual vectors, the solve readout value, the 4 px underline under her name, one marker on the final card |
| Lime glow | `rgba(198,255,61,.35)` | 1-frame flash halo on the solve only |

The SF logo is rendered **silver**: greyscale, contrast-shaped, mapped `#1A1A1C` to `#F4EFE6`, alpha kept (test: `logo_silver_test.png`, `look_test.png`, which reads as chrome and premium). No red anywhere in the piece.

**Plate grade (colour dept, one `.cube` or one ffmpeg chain):**
`hue=s=0` → `curves=master='0/0 0.12/0.03 0.5/0.48 0.85/0.9 1/0.97'` (crushed toe, soft shoulder) → warm-paper tone `colorchannelmixer=rr=1.0:gg=0.985:bb=0.95` (applies a slight warmth to the highlights only, because the shadows are near zero) → `vignette=PI/4.5` → `noise=alls=7:allf=t`. Plus `gblur=sigma=1.2` at 1080 (the source is a 302 px wide crop scaled up; the grain and slight softness read as film, not as upscale mush).
**QC:** `signalstats` on the plate: mean |U-128| and |V-128| ≤ 2 on every frame; mean B ≤ mean R on the final.

## 6. Background shots (picture only; trailer active picture is `crop=1280:536:0:92`)
Vertical crop `crop=302:536:CX-151:92`, then `scale=1080:1920:flags=lanczos`, then the grade. 23.976 → 25 fps with `fps=25` (or `minterpolate` for the slowed clips, `mi_mode=blend` if `mci` warps). All are verified in B&W in `crop_test_bw*.png`. None overlaps Vinay's 37-52 / 94 / 119 / 124-126 / 136 / 142-147.

| # | t (frames) | trailer src (s) | speed | CX | what / why | transition IN (on the beat) |
|---|---|---|---|---|---|---|
| P1 | 0.00-2.00 (0-49) | 30.70-31.55 | 0.425x | 770 | **Chun-Li alone** in the dark warehouse, hair buns, a column of window light. Push-in 1.00→1.06. Frame 0 must show her clearly (no black first frame) | none, starts at 60% |
| P2 | 2.00-3.40 (50-84) | 32.75-33.55 | 0.57x | 740 | silhouette fall/kick in hard window shafts | 6-frame luma-wipe dissolve (bright areas first) |
| P3 | 3.40-4.60 (85-114) | 108.65-109.30 | 0.54x | 680 | slatted-window dojo, staff fighter silhouette | dissolve 4 fr on hit 3.44 |
| P4 | 4.60-6.04 (115-150) | still 112.80 | **depth.py parallax**, dolly-in, 1.44 s, amount 0.8 | 660 | vertical warehouse, a fighter leaping up through a well of steel and light. **This is the 2.5D moment** and it echoes the 3D camera of the names | dissolve 4 fr on hit 4.60 |
| P5 | 6.04-7.80 (151-194) | 147.95-148.80 | 0.48x | 610 | fighter thrown across a floor lit by window light (the loudest drum is the cut) | 2-frame white flash (ivory 40%) on 6.04 |
| P6 | 7.80-9.20 (195-229) | 117.85-118.45 | 0.43x | 720 | backlit slats, two silhouettes bent over a box | dissolve 6 fr |
| P7 | 9.20-10.84 (230-270) | **150.20-151.82, 1.0x, SYNC** | 1.0x | 720 | crouching fighter in smoke. **From here the picture runs at the trailer's own timecode, locked to the music** (src = 141 + t). That is the matchmove pun: the plate is "in sync" | dissolve 8 fr |
| P8 | 10.84-13.00 (271-324) | **151.82-153.94, 1.0x, SYNC** | 1.0x | 770 → 820 (ease pan 152.60-153.00, following her) | **Chun-Li close-up**: the trailer's own cut on the hero hit. The point cloud registers onto it | **hard cut** (the trailer's own, frame 271) |
| P9 | 13.00-15.00 (325-374) | 33.75-34.75 | 0.5x | 760 | Chun-Li small and still, standing by the arched window in the warehouse. **Bookends P1** | 4-frame ivory flare (see 13.0) |

Plate opacity (animated in HyperFrames): P1 0.70 · field 2.0-9.2 0.45 (names lead) · breath 0.35 · solve 10.84 0.75 snapping down to 0.55 by 11.6 · 12.2-13.0 0.40 · title 0.28.
Render `bg_plate_1080.mp4` (CRF 14, exactly 375 frames). The editor also extracts `hero_1080.png` = P8 at src 151.90 (CX 770, graded) for the point cloud.

## 7. The 3D system (mograph)
World units = px at z=0. Camera focal f = 2600 px (about a 34 mm feel on a 9:16 frame), principal point (1080, 1920).
`project(X,Y,Z)`: transform into camera space (yaw, pitch, roll, position), then `sx = 1080 + f*Xc/Zc`, `sy = 1920 + f*Yc/Zc`, `scale = f/Zc`.

**Names (source/credits.txt, verbatim, 89 names: 45 left, 44 right).** Their solved positions are the real DNEG layout: left column right-aligned at x = -45, right column left-aligned at x = +45 (relative to the list centre), row pitch 96. The world is shifted so that **SUKANYA DILIP DHARIYA (right column, row 29) is centred at (0,0,0)**, which puts her at the frame centre when solved.
Each name i also has an *unsolved* depth offset `dz_i` (seeded random in [-5200, +1400]) plus a small `dx_i, dy_i` (±260). Her `dz` = -4800 (far: she is the vanishing point the camera flies toward).
`position_i(t) = solved_i + (1 - s(t)) * offset_i`, where `s(t)` is the solve progress (0 before 9.2, easeInOutQuart to 1.0 at exactly t=10.84, so the final 3 frames move fastest).

**Camera path** (Catmull-Rom on keyframes, all eased, no linear moves):
| t | position (x, y, z) | yaw / pitch / roll | note |
|---|---|---|---|
| 2.00 | (0, 1600, 4200) | 0 / 4 / 0 | names start behind the camera and stream past the lens |
| 6.04 | (-300, 600, 1500) | 14 / 6 / -1.5 | accelerating forward through the field |
| 9.20 | (-900, 0, 2600) | 35 / 12 / -2 | oblique: the field reads as a vast tilted sheet receding into fog |
| 10.84 | (0, 0, 2600) | 0 / 0 / 0 | **SOLVED frontal pose**; at z 2600 with f 2600, scale = 1.0 |
| 13.00 | (0, 0, 3300) | 0 / 0 / 0 | slow dolly back |
Micro-impulses on the drive hits (2.80, 3.44, 4.60, 6.04, 7.80, 8.20, 8.80): +60 units of forward z over 3 frames with an ease-out decay. They are felt, not shaken. No camera shake anywhere.

**Per-name rendering:** Archivo 500 caps, 56 px at scale 1, letter-spacing 0.06em, colour Pearl `#D9D5CC`. Opacity = fog(Zc) (0 beyond z 9000, full inside 3500). Blur = min(10 px, |Zc - focusZ| * 0.0025) (depth of field, focusZ follows her name). Names closer than z 400 fade out (no giant letters filling the screen). Plain CSS filter blur; no `will-change` (it would rasterise the text small and blur it).

**Track markers and residuals (canvas, Solve Lime):** each name has a 14 px "+" at its anchor (the start of the text for the right column, the end for the left column). From 2.0 to 10.84 a 2 px lime line runs from the marker's current projected position to where its *solved* position would project. These are the reprojection residuals. They are long and chaotic in the field act, shrink with s(t), and are **exactly zero at 10.84**. Lime opacity 0.55, and 0.9 for hers.

**Point cloud (canvas):** depth-art builds it from `hero_1080.png`: `depth.py map hero_1080.png hero_depth.png`, then take about 2,800 points on luminance edges (Sobel top 6%) plus 600 random points, each with (u, v, depth, luminance). They are unprojected with the same f so that at the solved pose they reproject onto their own pixels: `points.json`. They are visible 9.20-11.30 as 3 px ivory dots (Pearl, alpha = luminance * 0.8) sitting in the 3D world behind the names (z 2600-5200). The point cloud orbits with the camera, so you see Chun-Li's face as a 3D sculpture of dots from the side, and at 10.84 the dots land *exactly* on her face in the plate. Then the dots fade over 0.45 s while the plate rises to 0.75.

**Lens grid (Act I):** canvas, a 22x40 cell grid of 2 px Ivory hairlines at 20% opacity, barrel distortion `r' = r(1 + k1 r^2)` with k1 animating from -0.22 to 0 between 0.49 and 1.85 (easeInOutCubic). Brighten to 38% on frame 12, then fade out over 1.85-2.10 as the names arrive.

**HUD (IBM Plex Mono 400, 30 px, Silver, lime for the values only), bottom-left x 160, y 3020; two lines, no more:**
- 0.0-2.1: `LENS  ·  K1 -0.2200` → counts to `K1 0.0000  UNDISTORTED`
- 2.1-10.84: `SOLVE  ·  89 TRACKS  ·  ERR 41.60 px`, where ERR = 41.6 * (1 - s(t)) + 0.18 (stays at 41.60 until 9.2, then counts down)
- 10.84-12.2: `SOLVED  ·  ERR 0.18 px` (value in lime), then fade out
(These are graphic readouts of the visual metaphor, not claims about her work. No other numbers, years or roles anywhere.)

## 8. Typography (Google Fonts, all HTTP 200 checked; load with `<link>` and wait for `document.fonts.ready`)
- **Bodoni Moda 500** (display serif, prestige film title): her name on the title card.
- **Archivo** (variable width): field names at width 100 / weight 500; role and studio lines at **width 125 (expanded) / weight 600**.
- **IBM Plex Mono 400**: HUD only.
- Offline fallback: Playfair Display, then serif, for the name; Inter for the sans; DejaVu Sans Mono for the HUD.

**The name sequence (the heart of the piece):**
- 10.84 (f271): her field name is at frame centre, scale 1.0, Ivory `#F4EFE6`, 100% opacity, blur 0. All the other 88 names drop to 22% opacity over 6 frames (their sharpness stays, so the list is still readable). A **lime 4 px underline** draws left to right under her name in 5 frames. Her "+" marker gets a 1-frame lime glow. A one-frame full-frame flash of `#F4EFE6` at 18% sells the snap.
- 11.30-12.20: the camera dollies back (the list shrinks and dims into fog) while her name *comes forward in z* (it detaches from the plane, scale 1.0→1.8). During 11.60-12.10 it **rack-focuses**: the Archivo field name blurs out (0→14 px) while the Bodoni title blurs in (14→0 px) in the same place. A focus pull is the transition; there is no morph and no slide.
- **Title layout (final, 2160x3840; safe area x 160-2000, y 400-2950):**
  - `SUKANYA`: Bodoni Moda 500, about 300 px, letter-spacing 0.05em, Ivory, centred at y ≈ 1760
  - `DILIP DHARIYA`: Bodoni Moda 500, about 190 px, letter-spacing 0.08em, Ivory, y ≈ 2010. **Auto-fit:** measure with `getBoundingClientRect` and scale so that the widest line is ≤ 1760 px.
  - Lime underline (moves up from the field name), 520 x 4 px, y ≈ 2120, centred
  - `SR. MATCHMOVE ARTIST`: Archivo 125/600, 76 px, letter-spacing 0.32em, Ivory 92%, y ≈ 2290. Fades in and rises 24 px, 12.10-12.60
  - **13.01:** silver SF logo (sf_logo_alpha → silver), 1180 px wide, centred, y 760-1290. It **does not scale-slam**. An ivory anamorphic streak (a 3840 x 40 px horizontal gaussian, screen blend) sweeps left to right across the logo in 8 frames, revealing it with a soft mask that follows the streak. This echoes the trailer's own title flare, which sits under it: the editor can screen-blend the trailer's 153.95-154.30 flare frames (B&W, at 50%) here.
  - `STREET FIGHTER  ·  DNEG`: Archivo 125/500, 58 px, letter-spacing 0.42em, Silver `#A9A9A6`, y ≈ 2420, 13.20-13.60
  - 13.0-15.0: everything holds. Whole-card push-in 1.000→1.025. A last tiny lime "+" sits left of the role line as a quiet signature. **No fade to black**: the last frame is a clean poster (loops well on Reels).
- Spelling check: `SUKANYA DILIP DHARIYA`, `SR. MATCHMOVE ARTIST`, `STREET FIGHTER`, `DNEG`. Nothing else is invented.
- Verify credits.txt row 1 (`SAMITH SOUMYANATH | SIDDHANT SUNIL SONAWANE`) against `review/freeze_x4.png` / movie.mp4 at about 62 s before the build. It was partly cut in the source. If it is unverifiable, drop that row (88 names) rather than guess.

## 9. Second by second
| t (frame) | Picture | Sound (one continuous trailer bed, 141-156) |
|---|---|---|
| 0.00 (0) | P1 Chun-Li in the warehouse at 70%; barrel lens grid over her; HUD `LENS · K1 -0.2200` | bed in (3-frame fade) |
| 0.49 (12) | grid brightens; the un-distortion begins | first hit |
| 0.5-1.85 | the grid straightens like a lens being solved; slow push on her | intro |
| 1.85-2.10 | grid fades; the first names rush past the lens out of the dark | |
| 2.00 (50) | luma-wipe → P2; camera flying forward inside the name field; lime residuals everywhere | drive begins |
| 2.80 / 3.44 | dolly impulses; P3 at 3.40 | hits |
| 4.60 (115) | P4: 2.5D depth parallax up the steel well; the field and the plate both have depth now | hit |
| 6.04 (151) | ivory flash → P5; the camera starts arcing to the oblique view | loudest drum |
| 7.80 (195) | P6 backlit slats; the field reads as a huge tilted sheet of names receding into fog | hits 7.80 / 8.20 / 8.80 |
| **9.20 (230)** | P7 **in sync** (crouch in smoke). The point cloud (Chun-Li's face as dots, seen from the side) appears among the names. The camera decelerates and swings toward frontal; the depth offsets start collapsing; the residuals shrink; ERR counts down | **the breath** (the music dips) |
| 10.2-10.8 | almost aligned: the names nearly line up in two columns, the point cloud nearly forms a face | quietest point, then the pickup |
| **10.84 (271)** | **SOLVE.** Everything snaps flat in one frame. The trailer cuts to Chun-Li and the dots land on her face. The list is legible in two columns. **Her name is at dead centre**, ivory, with a lime underline. `SOLVED · ERR 0.18 px` | **HERO HIT** (151.84) |
| 10.9-11.3 | dots fade; the plate rises; the other names settle at 22% | sustain |
| 11.3-12.2 | dolly back; her name comes forward; focus pull Archivo → Bodoni title | |
| 12.1-12.6 | `SR. MATCHMOVE ARTIST` rises in | |
| **13.01 (325)** | **TITLE**: ivory streak sweeps; the silver logo is revealed; P9 Chun-Li by the window at 28% | **the trailer's own title stinger** (154.01) |
| 13.2-13.6 | `STREET FIGHTER · DNEG` | |
| 13.6-15.0 | poster hold with a slow push | tail; fade 14.3→15.0 |

## 10. Sound plan: ONE real trailer bed, nothing synthetic
- `source/trailer.mp4` **141.00-156.00 s** (`atrim=141:156,asetpts=PTS-STARTPTS`), stereo 48 kHz, uninterrupted from frame 0 to 375. A 3-frame fade in (141.0 is already quiet, -33 dB) and a 0.7 s fade out from 14.3.
- **The picture is cut to the music; we add nothing to the picture.** The bed already contains every accent: 0.49, the drive hits, the breath, the hero hit at 10.84 and the title stinger at 13.01.
- Creative move (different from Vinay's low-pass): **the "converging" stereo.** During the breath (9.20-10.84), narrow the bed's stereo width from 100% to about 35% (`stereotools=mlev`/`slev` automation, or a mid/side crossfade). The image collapses toward the centre as the solve converges, then **snaps back to full width on frame 271**, exactly when the picture snaps. The ear feels the solve without any filter colour or added sound. Width only; no EQ, no level dip beyond the music's own.
- Optional, and only if the hero hit feels thin on phone speakers: a sub reinforcement at 10.84 and 13.01 (`impact.wav` through `lowpass=f=90` twice, -16 dB under the bed, ≤0.6 s). If anyone can hear it as a separate sound, delete it.
- **Banned:** every synthetic sfx (shimmer, riser, whoosh, swipe, glitch, tape-stop, chime, drone) and tick sounds for the trackers.
- Master: -14 LUFS integrated, ≤ -1 dBTP after AAC (`tools/vfx/bin/master_audio.sh`). QC: the hero transient must sit on frame 271 ±1 and the stinger on 325 ±1 (`hyperframes audio` onsets).

## 11. The Short / thumb-stop
The piece is the Short. **Thumb-stop: 9.2-11.0.** A cloud of names and a face made of dots rotate in 3D, then everything snaps flat into a perfect credit list with one name at dead centre, on the hit, as Chun-Li appears. Frame 0 is already strong (Chun-Li in a light shaft behind a curved lens grid), never black.
Cover frame: **t = 14.4** (silver logo, ivory serif name, lime rule, Chun-Li in the window).

## 12. Build plan (4 cores, about 1.5-2 h wall clock). One owner per department; heavy jobs ≤ 2 at a time.
| # | Dept | Task | Output (`shots/sh010/<dept>/v001/`) | Est. |
|---|---|---|---|---|
| 1 | **edit** | Cut P1-P9 per `cues.json` (crop, retime, `fps=25`), the luma-wipe/dissolve/flash transitions, P7/P8 at 1.0x in sync. Export `hero_1080.png` (151.90, CX 770). Verify credits row 1 | `bg_plate_raw_1080.mp4` (375 fr), `hero_1080.png` | 15 min |
| 2 | **depth** (roto/depth artist) | `depth.py parallax` on the 112.80 still (1080x1920, dolly-in, 1.44 s = 36 frames, ~15 s compute). `depth.py map hero_1080.png`, then a numpy script → `points.json` (~3,400 pts) | `p4_parallax.mp4`, `hero_depth.png`, `points.json` | 15 min, in parallel with 1 |
| 3 | **color** | Silver-gelatin chain (section 5) → `silver.cube` + graded `bg_plate_1080.mp4`; silver logo PNG at 2160 wide; chroma QC | `bg_plate_1080.mp4`, `sf_logo_silver.png`, `silver.cube` | 10 min |
| 4 | **mograph** | HyperFrames, 2160x3840, `data-fps=25`, `data-duration=15`. Layers in section 4; JS camera and projection (section 7); DOM names; canvas grid/points/residuals; title; HUD. First a proxy render (540x960) of the full 15 s plus `snapshot`s at 0.3 / 1.2 / 3.0 / 7.0 / 9.6 / 10.5 / **10.84** / 11.8 / 12.4 / 14.4 s for director review. Then the final native 4K render, run alone | `sukanya_v001_4k.mp4` (video only) | 45-60 min (render ~15-20 min at 4K) |
| 5 | **sound** | Bed cut, stereo-width automation, master, onset QC | `bed_master.wav` | 10 min, in parallel with 4 |
| 6 | **comp/delivery** | Mux, frame-count check, 4K master + <16 MB share copy (H.264, 2-pass, ~8 Mbps) | `deliver/Sukanya_Dilip_Dhariya_StreetFighter_SrMatchmove_4K.mp4`, `..._share.mp4` | 10 min |
| 7 | **director** | Review proxy (stills above) → notes → final review | `review/director_v001.md` | 10 + 10 min |

Critical path: 1 → 3 → 4 (4 can start on the camera/names system with a placeholder plate, while 1-3 run).

**QC gates:** 2160x3840, 25 fps, 375 frames, 15.00 s; hero solve exactly frame 271 (the names flat, the residuals zero, the dots on the face, the trailer's cut); title on 325; the name spelled exactly; the plate is chroma-free (no blue anywhere; lime only in graphics); type crisp at a 100% crop (native 4K DOM text, never an upscaled raster); no black frame 0; no frame where the names jitter (the camera is evaluated from time, never from requestAnimationFrame).

## 13. Risks and fallbacks
- **CSS-filter blur on 89 DOM names makes the 4K render slow**: quantise the blur to 6 levels, and skip the filter when the blur is < 0.5 px. If it is still slow, draw the field names on the canvas (`fillText` at 4K is also native-sharp) and keep only her name and the title as DOM.
- **The point cloud reads as noise**: raise the edge share to 80% and the dot size to 4 px; the face must be recognisable by about 10.2.
- **The soft 302 px plate**: it sits at 28-55% under sharp type with grain, which reads as film. Do not sharpen it (halos).
- **Bodoni Moda caps are too wide for DILIP DHARIYA**: auto-fit (section 8). Never go under 150 px.
