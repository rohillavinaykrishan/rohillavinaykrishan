# Treatment v3 - "THE SOLVE"
Vinay Krishan Rohilla - Sr. Matchmove Artist - DNEG - Street Fighter
15.0 s, 2160x3840, 25 fps (375 frames), ONE final output.

Director data (inputs, not reports): `shots/sh010/director/v001/`
- `mood_music_bed_61-87.json`: song_mood on the chosen music window
- `trailer_dialogue_words.json`: whisper transcript of the trailer, used to find dialogue-free music
- `bg_candidates_activepic.png`: the candidate shots, full active picture, timestamps burned in

---

## 1. Logline
The trailer is in the background, the crew roll scrolls over it, and like a matchmove artist locking a track,
the roll slows down and "solves" onto one name: VINAY KRISHAN ROHILLA.

## 2. What the material says
- No lyrics. The music is the trailer score. The window **61.0-76.0 s** has no dialogue at all
  (the transcript has a gap from 59.6 to 87.0 s): D minor, ~117.5 BPM, a pulsing build with a clear shape:
  - t=1.0 (trailer 62.0): first hit after a near-silent 1 s dip, so the piece opens on a hit.
  - t=1.0-7.75: steady rise. Loudest stretch is 67.0-68.75 (t=6.0-7.75).
  - t=8.0-8.75 (69.0-69.75): a dip. The music takes a breath.
  - t=10.20 (onset 71.18-71.22, measured at 40 ms resolution): the loudest single hit in the window (-9 dB). **The name lock goes here: frame 255.**
  - t=11.94-12.22 (72.94-73.22): true silence (-36 dB). **The picture freezes here.**
  - t=12.28 (onset 73.26-73.34): the drop. Full energy until the end. **The title card slams in here: frame 307.**
- song_mood suggests "moody / dark / noir" (minor key, heavy). We keep the weight and the deep blacks but
  **reject the cool shadows**. The client asked for warm, and Street Fighter's own identity is red-orange-gold
  key art. So the grade is "heavy and dark, but fire-lit."
- Emotion (no lyrics, so the arc comes from the client's goal, which is pride): anonymous crowd (one name
  among hundreds), then focus and search, then recognition (the lock), then a confident signature (the title card).
  The feeling is quiet pride. It should not feel like bragging. The roll stays respectful of the whole team
  ("Thanks to our talented teams!" stays on screen) and then the camera finds him.

## 3. Arc
| Section | t (s) | Emotion | Energy |
|---|---|---|---|
| Intro | 0.0-1.0 | anticipation, a lone fighter in a light shaft | low, rising |
| "Verse": the roll | 1.0-7.7 | the team, the scale of the film, fights hitting on the beat | mid to high |
| "Bridge": the search | 7.7-10.2 | slow motion, the roll decelerates, trackers hunt | held breath |
| Hook: the lock | 10.2-11.95 | recognition, his name solves and glows | peak (single hit) |
| Final: title card | 12.28-15.0 | pride, signature, hold for reading | full, then a 0.7 s music tail fade |

## 4. Visual world
- Three layers, always on screen. No hard cuts between "sections" (the v1/v2 mistake):
  1. **Base:** the red grunge key-art texture (crop from `review/logo_x4.png`, the empty red field between
     y≈1200 and 3300 in its 2880x5120 frame), scaled to fill and darkened to ~35%. Its job is to make the
     background read as "transparent footage over the film's poster red", not as footage over black.
  2. **Background plate:** trailer fight shots, vertical crops, warm gradient-mapped, blurred slightly (depth
     of field), drawn at 35-75% opacity over the base. Transitions only by dissolve, light leak or motion-blur
     whip, on beats.
  3. **Typography / HUD:** crisp vector type rendered natively at 2160x3840 (HyperFrames): the SF logo, the
     header, the 2-column roll, trackers, then the title card. Ember particles drift between layers 2 and 3.
- Style references: big-budget fight-film end credits, poster-red key art, tungsten arena light shafts,
  dust in backlight. Premium and restrained, with no gaming-HUD clutter.
- **Signature idea (his craft): "the track solve."** While the roll slows down, 6-8 small 2D trackers
  (a pattern box plus a dashed search box and a "+" centre, thin amber lines) attach to names. They move
  with the roll at exactly its velocity, so they look truly locked: an honest matchmove gag. One by one they
  go red and drop ("lost track"). The last one is on his name. At the music hit its four corner brackets snap
  tight, a tiny mono label reads `TRK_07  SOLVED`, and a small burst of gold point-cloud sparkles comes off
  the name. That is the only HUD moment, on screen from about 7.9 to 11.96 s. Nothing cheesy: no scan
  lines, no green and no sci-fi text walls.

## 5. Color direction
Grade family: **"fire-lit dark": deep warm blacks, blood red mids, orange-gold highlights. Zero blue.**
Same grade from start to end, so continuity comes from the color. Only the opacity and exposure of the
background change per section.

Palette:
| Role | Hex |
|---|---|
| Night black (deepest bg) | `#070303` |
| Ember shadow | `#3A0D08` |
| Blood red | `#8E1A0E` |
| Street Fighter red | `#C8161D` |
| Fire orange | `#F05A1A` |
| Gold (highlight, tracker, rule) | `#F5B53C` |
| Pale gold (name fill top) | `#FFE7B0` |
| Ivory (roll names) | `#F3E6D6` |
| Dimmed names | `#9C8B7E` |

**How to kill the blue (the v2 complaint), guaranteed:** generate one 33-point `.cube` LUT in Python and apply
it with ffmpeg `lut3d` to the whole plate after the transitions:
- luma Y = 0.2126R + 0.7152G + 0.0722B, mapped through the gradient
  `0.00 #050202 → 0.25 #3A0D08 → 0.50 #8E1A0E → 0.72 #E0581A → 0.90 #F5B53C → 1.00 #FFE7B0`
- out = 0.72 × gradientmap(Y) + 0.28 × warm(original), with warm = (1.05R, 0.92G, 0.55B)
- clamp B ≤ G ≤ R at the end. Every pixel lands in the red-gold family, including the blue neon
  sources and the green desert hills.
- Bonus: white "fadewhite" flashes through the LUT come out pale gold, which gives the light leaks for free.
- QC: `signalstats` on the final, where the mean of B minus R must be negative on every frame.

## 6. Background shots (all inside the active picture crop=1280:536:0:92)
Vertical crop = `crop=302:536:CX-151:92` (full active height, 9:16), then `scale=1080:1920:flags=lanczos`.
The plate is built at 1080x1920. It is dimmed and blurred, so 1080 is enough, and HyperFrames scales it to 4K
under the crisp type. No Real-ESRGAN on the plate.

| # | t in-out (frames) | trailer src (s) | speed | crop CX (in 1280) | what we see / framing intent | transition IN |
|---|---|---|---|---|---|---|
| A | 0.00-1.00 (0-25) | 36.72-37.48 | 0.76x | 900 | Ken in red, seated silhouette in a hard light shaft. Push-in 1.00→1.05 | starts at 60% (no black first frame) |
| B | 1.00-2.90 (25-72) | 37.55-39.45 | 1.0x | pan 380→720 | Ken vs Dhalsim clash in the arena; pan follows Ken to the floor | light leak, 6 fr, centred on 1.00 |
| C | 2.90-3.83 (72-96) | 39.65-40.58 | 1.0x | 540 | Dhalsim (red head paint) punching toward lens | motion-blur whip (`hblur`) 4 fr |
| D | 3.83-4.80 (96-120) | 40.95-41.85 | 0.93x | 590 | Ken airborne, blond hair exploding against window light | dissolve 4 fr |
| E | 4.80-5.73 (120-143) | 50.15-51.08 | 1.0x | 720 | Boxer's red glove punch into lens (low angle) | light leak 6 fr (music hit at 4.75) |
| F | 5.73-6.71 (143-168) | 52.02-52.78 | 0.78x | 700 | Boxer vs Ken, Ken mid-air, arena crowd | whip 4 fr |
| G | 6.71-7.73 (168-193) | 123.72-124.28 | 0.55x | 600 | Orange fire-lit scream, push-in 1.00→1.08 (energy peak) | light leak 6 fr |
| H | 7.73-9.24 (193-231) | 125.00-126.50 | 1.0x | 590 | Desert fight, red gi, dust (hills turn bronze through the LUT) | dissolve 8 fr (energy settling) |
| I | 9.24-12.28 (231-307) | 135.75-137.21 | 0.5x | 650 | Two fighters leaping in golden arena light. Slow-motion "hang time" under the name lock. Freeze on frame 299 from 11.96 to 12.28 (frames 299-306, the music's silent beat) | slow dissolve 10 fr |
| J | 12.28-15.00 (307-375) | 146.20-147.85 | 0.6x | 640 | Fighter slamming down onto the arena floor, sand in light. Under the title card | gold flash 4 fr (the slam) |

- Slow-motion clips (A, D, F, G, I, J): `setpts=PTS/speed` then `minterpolate=fps=25:mi_mode=mci` (or `mi_mode=blend`
  if mci warps; the plate is blurred anyway). Normalise all clips to 25 fps before `xfade`.
- Avoided on purpose: every blue/neon shot (0-20 s, 84-100 s, 129-134 s, 143 s Ryu, 149-153 s), the 94.5 blue
  walk-in that opened v2, and all dialogue close-ups.
- Plate finishing after the LUT: `gblur=sigma=3` (at 1080), vignette (PI/4.5), light film grain `noise=alls=6:allf=t`.
  Render `bg_plate_1080.mp4` (CRF 14, exactly 375 frames).
- **Background opacity over the red base** (animated in HyperFrames): 0.0-1.0 → 0.75; 1.0-8.0 → 0.55;
  8.0-10.2 → 0.45 (focus moves to the type); 10.2-12.28 → 0.35; 12.28 flash 0.90 decaying to 0.30 by 12.8; 0.30 to the end.

## 7. Typography direction
Google Fonts **is reachable** (`curl -sI .../css2?family=Bebas+Neue` → HTTP/2 200). Use `<link>` in HyperFrames:
- **Bebas Neue** for the title name (cinematic condensed caps).
- **Oswald 600** for the header "Thanks to our talented teams!" (mixed case, condensed, the same feel as the DNEG reel).
- **Inter 500/600** (installed) for the roll names, role line and DNEG line.
- **JetBrains Mono 500** for the tiny tracker labels only.
- Fallback if offline: Inter Display 800 with letter-spacing -0.01em for every display line.

Layout at 2160x3840 (Reels safe area: keep key text between y 400 and 2950, and x 160-1900 for the title card):
- **SF logo**: key it out of `review/logo_x4.png` (crop about x 640-2230, y 120-950 in the 2880x5120 frame;
  alpha = smoothstep of max(R,G) minus a red-floor key in numpy, then a 1 px feather). Placed at y 300-950,
  1500 px wide, from frame 0 to the end. **It never moves**, which keeps everything continuous.
  0.0-1.0 at 45% opacity, slam to 100% plus a gold bloom at 1.0.
- **Header** "Thanks to our talented teams!": Oswald 600, 112 px, ivory, y≈1060, visible 1.0-11.96, fades out over 11.96-12.28.
- **Roll** (source/credits.txt, verbatim, keep the letter-group gaps):
  Inter 500, 52 px, caps, letter-spacing 0.03em, ivory `#F3E6D6` at 85%. Left column right-aligned to x=1035,
  right column left-aligned at x=1125. Row pitch 112 px, and a blank row (112 px) between letter groups.
  The roll window is y 1180-3300, with 220 px soft alpha masks at the top and bottom (names fade under the header).
  Row indices: S 0-4, gap 5, T 6-11, gap 12, U 13, gap 14, V 15-30 (**VINAY KRISHAN ROHILLA = right column of
  row 19**), gap 31, Y 32-36, gap 37, Z 38.
- **Roll motion, the deceleration:** `y_row(i,t) = y0(t) + 112*i`, with
  `y0(t) = 2700 - 2908 * easeOutCubic((t - 1.0) / (T_LOCK - 1.0))` for 1.0 ≤ t ≤ T_LOCK, constant after.
  **T_LOCK = 10.20 s (frame 255)**, measured from the bed (onset 71.18-71.22). Re-check with `hyperframes audio` after
  the mix and move it by one frame at most. Row 19 then sits exactly on y=1920 (frame centre). Start speed is about 38 px/frame
  at 4K and decays smoothly to 0. Add a tiny vertical motion blur (filter blur ∝ speed, max 2 px) on the roll only.
  Before t=1.0 the roll is hidden.
- **Trackers** (7.9-10.2): 7 widgets on names in rows 11-27, pinned to their names' y(t). Each one is a 110x70 pattern
  box (solid 3 px) plus a 230x150 dashed search box, a "+" centre and a label `TRK_0n` (JetBrains Mono 26 px), in
  gold `#F5B53C`. They appear staggered at 7.9 / 8.2 / 8.5 / 8.8 / 9.1 (scale 1.3→1.0 in 4 frames). Between 9.0 and 9.9
  six of them turn `#C8161D` and fade ("lost track"). TRK_07 sits on his name the whole time.
- **The lock (T_LOCK)**: four gold corner brackets snap from ±60 px to tight around the name (3 frames, ease-out-back).
  The name turns into a gold vertical gradient (`#FFE7B0`→`#F5B53C`), Inter 700, scaling 1.00→1.28 with a slight
  overshoot over 8 frames, glow `0 0 40px rgba(240,90,26,.6)`. A burst of 40 gold point-cloud dots, life 0.6 s.
  Label `TRK_07  SOLVED` appears under it. All other names rack-focus away: opacity to 22% and blur 3 px over 12 frames.
  10.6-11.4: the solved name glides from the right column to the horizontal centre, as the solved camera re-centres on its track.
- **Title slam (12.28, frame 307)**: the roll and trackers whip upward out of frame (translateY -600, blur 8 px, 6 frames).
  The centred gold name morphs into the title (crossfade with a 3-frame gold flash and a 6-frame camera shake of ±12 px):
  - `VINAY KRISHAN`: Bebas Neue 300 px, ivory, y≈1700
  - `ROHILLA`: Bebas Neue 300 px, gold gradient, y≈1990
  - gold rule, 1000x4 px, draws out from the centre 12.45-12.85, y≈2200
  - `SR. MATCHMOVE ARTIST`: Inter 600, 92 px, letter-spacing 0.22em, ivory, fades and rises in 12.55-12.95, y≈2330
  - `STREET FIGHTER  ·  DNEG`: Inter 500, 72 px, letter-spacing 0.35em, `#F5B53C`, 12.85-13.25, y≈2480
  - Character line-up art (crop of `review/logo_x4.png` bottom, about y 3800-5120 → 2160x~990) rises from the bottom
    12.28-13.0 at full width, y 2850-3840, with a gradient top edge.
  - 13.0-15.0: hold, with a slow push-in of the whole card from 1.00 to 1.03. Embers rise. **No fade to black.**
    The last frame is a clean poster, which makes a good loop for Reels and a good LinkedIn thumbnail.
- Facts only: no year, no other roles, no invented credits.

## 8. Second by second
| t (frame) | Picture | Sound (real trailer bed, one continuous take) |
|---|---|---|
| 0.0 (0) | A: Ken in a light shaft, plate at 75%. SF logo at 45%. One amber "+" tracker drifts, searching | bed 61.00 s fades in over 0.15 s (its own low pre-hit swell) |
| 1.0 (25) | **Hit.** Light leak → B. Logo slams to 100% with bloom, header appears, roll starts fast | the bed's own hit at 62.03 + deep sub layer |
| 1-2.9 | B clash, pan follows Ken; names stream up | bed |
| 2.9 (72) | whip → C (Dhalsim punch) | bed only (cut sits on the beat) |
| 3.8 (96) | dissolve → D (Ken airborne) | |
| 4.8 (120) | light leak → E (glove into lens) | the bed's hit at 65.79 |
| 5.7 (143) | whip → F (boxer vs Ken) | |
| 6.0-7.7 | light leak → G at 6.71 (orange scream), energy peak | the bed's hits at 67.01 / 67.87 |
| 7.7 (193) | dissolve → H (desert); the roll is clearly slowing | |
| 7.9-9.1 | trackers pop onto names one by one (silent: picture only, no tick sounds) | **"focus" filter**: the bed is low-passed 20 kHz → ~1.8 kHz from 7.9 to 10.16 and gains +2 dB of low end, so the world goes muffled and tense |
| 9.0-9.9 | trackers go red and drop. The roll is crawling. Dissolve → I (slow-motion leap) at 9.24 | bed muffled; its own dip at 69.0-69.75 lands here naturally |
| **10.20 (255)** | **LOCK**: brackets snap, name glows gold, sparkles, other names rack-focus away | **the filter snaps fully open on the bed's loudest hit (71.2)** + the trailer's own punch impact + deep sub |
| 10.6-11.4 | solved name glides to centre. `TRK_07 SOLVED` | bed |
| **11.96-12.28 (299-306)** | the whole frame freezes (plate frame 299, type holds, embers stop) | **the bed's real silence (72.94-73.22)**. Leave it silent: this gap is what makes the slam land |
| **12.28 (307)** | **SLAM**: gold flash → J, roll whips out, title card forms, camera shake | **the bed's drop (73.3)** + deep sub layer |
| 12.45-13.25 | rule, role line, STREET FIGHTER · DNEG, line-up art rises | bed (no chimes) |
| 13.0-15.0 | poster hold, push-in, embers | bed full; its hit at 75.79 lands at t=14.79; fade out 14.3→15.0 |

## 9. Music and sound: ONE real trailer bed (client note on v2, binding)
v2 problem: the trailer music played first, then a synthetic "ting"/drone tune from our numpy SFX kit came in under
the credit list. It sounded cheap and broke the film's world. **v3 rule:**
- **One continuous bed** from `source/trailer.mp4`: **61.00-76.00 s** (`atrim=61:76,asetpts=PTS-STARTPTS`), stereo 48 kHz,
  playing uninterrupted from frame 0 to frame 375. 0.15 s fade in, 0.7 s fade out from 14.3. It is dialogue-free
  (Whisper gap 59.6-87.0 s) and already contains every accent the edit needs: hits at 62.03 / 65.79 / 67.01 / 67.87 / 71.2,
  real silence at 72.94-73.22, and the drop at 73.3. **The picture is cut to the music. We do not add sound to the picture.**
- **Banned**: `sfx/shimmer.wav`, `glitch.wav`, `riser.wav`, `swipe.wav`, `whoosh.wav`, `reverse.wav`, `tape-stop.wav`,
  `downlifter.wav` and any synthetic drone, tone or chime. No tick sounds for the trackers; they stay silent.
- **Allowed accents** (each must sit *under* the music, felt more than heard):
  1. **Deep sub hit** at t=1.03, 10.20 and 12.30: `sfx/boom.wav` or `impact.wav` through `lowpass=f=90,lowpass=f=90`,
     about −14 dB below the bed, length ≤0.8 s with a 0.3 s fade. If anyone can hear it as a separate sound, it is too loud.
  2. **The trailer's own punch impact** under the lock: `source/trailer.mp4` 142.78-143.10 s (dialogue-free window
     140.8-147.0; a hit transient at 142.84, −14 dB peak), with `highpass=f=120`, a 40 ms fade in and 120 ms fade out,
     about −8 dB under the bed and aligned so its transient sits on t=10.20. It belongs to the film's world, so it blends.
- **Creative sound move (using only the real music): the "focus pull."** As the roll decelerates and the trackers
  search (7.9 → 10.16), automate a low-pass on the bed (20 kHz → 1.8 kHz, exponential) so the music sinks as if heard
  through a wall. On frame 255 the filter snaps open (≤2 frames) exactly on the bed's hit at 71.2. The ear "solves" at the
  same moment as the picture. Implementation: render the bed twice (dry, and `lowpass=f=1800`), then crossfade dry→filtered
  from 7.9 to 9.6 with `acrossfade`/`volume` expressions and cut back to dry at 10.20. Alternatively, run ffmpeg
  `lowpass` with `sendcmd` frequency steps every 0.1 s. Either one is about 5 minutes.
- **Honour the silence** at 11.94-12.22: no hits, no sub, nothing. The freeze-frame and the silence happen together.
- Master: −14 LUFS integrated, −1 dBTP (`tools/vfx/bin/master_audio.sh`), AAC 320k. QC by ear at the lock and the drop,
  and check `hyperframes audio` onsets against frames 255 and 307 (±1 frame).

## 10. The Short / thumb-stop
The whole piece is the Short. The thumb-stop is **10.2-12.6**: a full screen of anonymous names slows, the trackers
die one by one, one tracker solves and his name ignites gold, and two beats later it slams into the title. Frame 0
already shows a fighter in a light shaft plus the burning logo (never a black first frame). Cover frame: **t=14.0**
(full title card, line-up art).

## 11. Build plan (4 cores, about 1 hour)
1. **Plate (ffmpeg), ~10 min**: 10 clips → `xfade` chain (fade / fadewhite / hblur) → `lut3d` warm.cube → blur, vignette,
   grain → `bg_plate_1080.mp4` (375 fr). Plate preview at proxy res first.
2. **Assets (python/numpy), ~5 min**: `warm.cube`, `sf_logo_alpha.png`, `lineup.png`, `red_base.png` from `review/logo_x4.png`.
3. **HyperFrames, ~30 min**: one composition at 2160x3840, `data-fps=25`, 15.0 s. Layers: red base, plate `<video>`
   with animated opacity, embers, logo, header, roll, trackers, title card. Run `hyperframes snapshot` at 0.5 / 2 / 7 /
   9.5 / 10.3 / 11 / 12.4 / 14 s at proxy before the full render. Final: `hyperframes render -q delivery -f 25`
   (render it alone, nothing heavy in parallel).
4. **Sound, ~10 min**: one bed + focus-pull filter + 3 sub layers + 1 trailer punch (`adelay`/`amix`) → master → mux. No other SFX.
5. **QC**: 2160x3840, 25 fps, 375 frames, 15.00 s, audio in sync (lock = frame 255 = bed hit 71.2, slam = frame 307 = bed drop 73.3); name spelled exactly
   `VINAY KRISHAN ROHILLA`; no frame where B > R on average; type sharp at 100% crop.
   Deliverable name: `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v3_4K.mp4`
   (plus an optional share-size encode of the same master).
