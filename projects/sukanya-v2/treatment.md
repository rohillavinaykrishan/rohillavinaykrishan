# Treatment v2: "SUPER ART"
SUKANYA DILIP DHARIYA · Sr. Matchmove Artist · DNEG · Street Fighter
18.0 s · 2160x3840 · 25 fps · **450 frames** · ONE deliverable: the 4K master (no share copy)
Written by the Director, 2026-10-23, 16:26-16:50 IST.

Director data (inputs for departments, not reports): `shots/sh010/director/v001/`
- **`cues.json`**: the **single source of truth for timing**: music window, the beat grid as frames, music events, every shot (trailer in/out, frame in/out, crop, characters, layer), palette, fonts, roll metrics. If this document and `cues.json` disagree, `cues.json` wins.
- `make_cues.py`: regenerates `cues.json` (edit the shot table there, never by hand).
- `audio/bed_client_116.30-134.30.wav` (the reference bed, 48 kHz), `audio/whisper_vadoff.py` + `whisper_client_vadoff.json` / `whisper_parallax_vadoff.json` (VAD-OFF checks)
- `sheets/overview_{0,60,120}.png` (whole trailer at 1 fps, active picture), `sheets/fine_*.png` (4 fps strips; the yellow stamp is seconds **after the strip start** in the file name), `sheets/selects_v001.png` (**every chosen shot, labelled**), `sheets/clash_143.3.png` (the fist-bump frame-step), `sheets/movie_roll_56.png`, `sheets/roll_64.0.png`, `roll_65.0.png`, `roll_pair.png` (the real roll, used to measure it)
- `fonts/` (Montserrat 500, Barlow Condensed 900 Italic + 600, Chakra Petch 600: TTFs from the Google Fonts CSS API)
- `lookdev/director_board_v001.png` + `board.html` (a style-frame mock of 4 key moments at 540x960: direction, not final art)

---

## 1. Big idea and logline
In Street Fighter, every fighter has a normal move set and one **Super Art**: the finisher that freezes the game, slashes a cinematic band across the screen and hits on the beat. A crew roll is a roster of hundreds of fighters. Ours scrolls exactly like the real one (real names, real order, real layout), with the film's fights flickering behind it. Then the music empties out, the roll stops, a **P1 select cursor** locks onto one row, Ryu's and Ken's fists close in slow motion, and on the drop **her name performs its Super Art**. It rips out of the roll, the roll's rows shatter outward to make way, a diagonal band slams across the frame, and the whole film **bursts from two-tone into full colour** inside that band. Eight fighters hit on eight beats behind her name, then it all folds into the title card.

**Logline:** *One name in a roll of hundreds gets selected, and gets the Super Art.*

**Emotional arc (no lyrics, so the arc comes from the purpose):** belonging (one of many, the real roll) → anticipation (the build, the cursor, the fists) → **arrival** (the drop, her name, colour) → pride (the roster fights for her) → signature (the title card).

### Why this is different from both earlier pieces
| | PARALLAX (her v1) | Vinay v4 GROUND TRUTH | **v2 SUPER ART** |
|---|---|---|---|
| Idea | a camera flying through floating names (matchmove metaphor) | a solved 3D monument in a real plate | **fighting-game grammar**: roster → select → Super Art → title |
| Roll | names scattered in 3D | a short duotone roll | **the real roll, flat, at real layout and speed** (what she asked for) |
| Footage | 1-2 soft B&W shots | 1 daylight beach plate | **21 shots, 9+ named characters**, layered in slash panels and a band |
| Colour | silver B&W + lime | sun-bleached sand + Marker Pink | **aubergine/saffron tritone that unlocks into full colour on the drop** |
| Type | Bodoni ivory | Unbounded / Inter Tight | **Barlow Condensed Black Italic + Montserrat + Chakra Petch** |
| Music | trailer 141-156 | trailer 112-127 | **her own track, 116.30-134.30** |
| Ending | dark, silver logo | light monument | **saffron-lit line-up art + gold-mapped logo** |

## 2. What the material says

### 2.1 Music decision: HER TRACK, `source/client_music.mp3` 116.30-134.30 s (18.0 s)
**Analysis** (librosa: 1 s summary over the whole track, then 20 ms and 10 ms RMS plus the sub band below 120 Hz and spectral flux; scripts in my scratch, results in `cues.json.events`):
- The track is wall-to-wall loud (-7.9 LUFS), so a "big hit" has to be a **contrast** event, not a loud one. I ranked every 0.5 s before/after jump. Candidates: 34.8 (+8 dB), 63.6 (+6 dB), **126.7**, 95.4, 139.4.
- **126.74 s is the textbook build and drop, and it is the only one with all three parts:**
  1. **Build** from 116.62: a hi-hat/top layer rises (+8 dB above 4 kHz) and stays.
  2. **Empty-out**: the sub band falls from 45 dB to 35 dB at 122.6 and returns briefly at 123.4. Then it **collapses to 19-21 dB from 125.6 to 126.4** (the bass is muted) under a 4-hit fill at 125.06 / 125.26 / 125.56 / 125.80 and a pickup at 126.48.
  3. **Drop at 126.74**: the sub band goes from 21 to 52 dB in 0.3 s (**+31 dB**), and full-band RMS reaches -6.2 dB, the loudest attack in the window. After it come 16 beats of full-energy groove.
- The window **116.30-134.30** starts on the build and puts the drop at **10.44 s = frame 261 exactly**. That leaves 10.4 s for the roll and the build, and 7.6 s for the Super Art and the title. 136 BPM = **11.03 frames per beat**. The beat grid (from `client_music_mood.json`, rebased) is f10, 21, 32, 42, 52, 63, 74, 84, 95, 105, 116, 126, 137, 147, 158, 168, 178, 188, 198, 209, 219, 232, 243, 254, **[drop 261]**, 266, 277, 289, 300, 310, 320, 330, 340, 350, 360, 370, 380, 392, 403, 415, 425, 437, 448. The drop attack sits 5 frames before the tracker's beat at f266, so **f261 is the hit**.
- **Whisper check, VAD OFF** (`audio/whisper_vadoff.py`: faster-whisper `small`, int8, `vad_filter=False`, word timestamps, `condition_on_previous_text=False`):
  - Her window returns a single segment, "THANKS FOR WATCHING!" (5.46-7.40 s, no_speech_prob 0.59, avg_logprob -0.76). That is Whisper's best-known hallucination on instrumental music; the track is a no-lyrics instrumental. **No vocals.**
  - The PARALLAX bed (trailer 141-156) returns voice-like content across the whole window, with **no_speech_prob 0.09**: crowd shouts and chant/count fragments ("5, 4, 1...", "4, 3, 2, 1...", "Evet!"). The brief bans spoken dialogue in the music, and that bed carries crowd voice throughout.

**Why her track wins:**
1. **It has a real hole-then-hit for the pop-up.** The pop needs a moment where the music *makes room*, and 125.6-126.4 is a true bass-out.
2. **It is hers.** She sent it, so hearing her own pick on her credit is a gift.
3. **It is clean.** No dialogue, and no crowd voice under the most important frame.
4. **It is different.** PARALLAX already used 141-156, and the brief asks us to be different from PARALLAX.
5. **The tempo suits the edit.** At 136 BPM there are 11 frames per beat, and its steady kick gives the Act 3 hit-per-beat chain a perfect grid.

What we keep from what she liked in PARALLAX's music: the dark, driving, minor-key mood. Her track is D minor and drives the same way.

### 2.2 The real roll (measured from `source/movie.mp4`, 720x1280)
- Layout: two columns, the left column **right-aligned**, the right column **left-aligned**, gutter centre at **x = 361/720** (slightly right of centre). Row pitch **23 px**, cap height about 11 px, a wide geometric sans (closest Google match: **Montserrat 500**, caps, tracking +0.02em). The "Thanks to our talented teams!" header stays fixed in a condensed bold.
- Scroll: her row is at y = 518 at 64.0 s and y = 401 at 65.0 s, so **117 px/s = 5.1 rows/s**.
- **4K re-set (native DOM text, never upscaled):** scale ×3 for 720→2160, then ×1.35 for phone legibility. Row pitch **93 px**, cap about **44 px**, gutter at **x = 1083**, scroll **19.0 px/frame** (474 px/s, the same rows per second as the real roll).
- Her row is `SHAHRUKH KHAN | SUKANYA DILIP DHARIYA`, row index 29 in `source/credits.txt` (0-based).
- **Gap to close (Roll dept):** at the real speed, the roll needs **about 56 rows above her row** to keep the window full from frame 0. `credits.txt` has only 29 (from SAMITH SOUMYANATH). The roll typesetters transcribe the **preceding rows from movie.mp4 56.0-63.5 s** (sharp 2x crops of single frames). Two agents transcribe independently and their results are diffed; **no invented names**, and any row they cannot read is dropped, not guessed. Fallback if fewer rows are available: start the roll at 70% speed and ease to 100% by f60.

### 2.3 The footage (I scanned the whole trailer at 1 fps, the fight sections at 4 fps, and the drop shot frame by frame)
The trailer is graded all over the map: blue rain alleys, magenta clubs, amber sauna, daylight beach, warm arenas. Cut raw at 9:16, that becomes a choppy slideshow. **The design answer is one colour system for everything (section 5) and big, layered, mostly wide framings.** We never use a 7x vertical crop.

Characters on screen (cross-checked with the Shot Librarian's `library/streetfighter-trailer/shots.json`, which landed at 16:29 IST): **Ryu, Ken, Dhalsim, E. Honda, Blanka, Guile, Cammy, Balrog, Chun-Li** (9 named), plus Vega? (B04), the aerial fighters (A02, B07) and the psycho-power energy shot (A09), which the librarian lists as unknown. That makes **21 trailer shots and 9+ characters in 18 s**, all inside single trailer cuts.

Avoided on purpose: the beach fight 124-127 (Vinay v4's hero plate), the B&W woman/wood-dummy shots around 24 s and 54 s (PARALLAX), logos/date cards (21-22, 93, 154-156, 167-168), and the Guile car scene (dialogue, no fight).

## 3. Visual world and motion language
- **World:** a fighting-game presentation layer over the film. The crew roll is the roster screen, the cursor is player select, the band is the Super Art cut-in, and the title is the victory screen. Everything is flat graphic planes in front of a deep, smoky, two-tone film world.
- **Personality:** **Energetic** (kinetic-sharp) for Acts 2-3, **Premium** holds for Act 1 and the title. Signature ease for entrances is `ease-out-expo` (`cubic-bezier(0.16,1,0.3,1)`); exits use `cubic-bezier(0.7,0,0.84,0)`. These are the only two eases, plus linear for the roll and ambient drift.
- **Base unit:** **1 beat = 11 frames** (enter 6 f = half a beat, hero moves 11 f, micro moves 3 f). Overshoot only on the name pop (6%) and the band slam (3%). Everything else lands flat.
- **Transition family:** hard cuts on beats inside panels and the band. The geometric family is **12° slashes only**: every panel, band, wipe and speed line runs at -12° (rising left to right). No dissolves, spins or circle wipes.
- **Hierarchy:** Act 1's hero is the roll, with footage as support. Acts 2-3's hero is her name, with the band as support and sparks/rings as texture. The title's hero is her name again. **One wow moment: f261.** Everything before it builds to it, and nothing after it tries to top it.
- **Depth (parallax):** background = smoke/grain/tritone plate bleed (0.2x), midground = slash panels / band footage (0.6x), foreground = type, cursor, sparks (1.0-1.3x).
- **Safe areas (9:16, 2160x3840):** top 470 px and bottom 700 px carry no critical type. The roll window is y 470-3060. Her hero name is centred at y = 1700, on the upper third (1280) to centre band, clear of the bottom UI.

## 4. Second-by-second timeline (25 fps; f = frame; src = trailer seconds)
Bed = her track 116.30-134.30. Shots and exact in/outs: `cues.json.shots`. Picture is always 2160x3840.

| t (s) | frames | Picture | Music |
|---|---|---|---|
| **ACT 1 ROSTER** | | | |
| 0.00-1.68 | f0-41 | Open on the **real roll already scrolling** (no fade from black: 3-frame fade-up only), Ki White Montserrat on Aubergine. Header `Thanks to our talented teams!` fixed at y 470-560 (Barlow Condensed 600, 64 px). Behind the roll is slash panel **P1** (2160x1180, skew -12°, centre y 1300) with **A01 Ken vs Dhalsim** knockdown in tritone at 60% opacity, drifting up at 0.6x roll speed | the build begins; hats rise f8 |
| 1.68-3.36 | f42-83 | Panel cut (hard, on beat f42): **A02 aerial kick through arena light shafts** (42% optical-flow slow-mo). A second, lower panel **P2** (centre y 2500) opens with a 6-frame slash wipe at f63 and carries A02's tail | beats 42, 52, 63, 74 |
| 3.36-5.04 | f84-125 | P1 **A03 E. Honda** stare (f84-104) → P2 **A04 red-jacket fighter vs silhouettes** (f105-125). Panels alternate upper/lower each 2 beats from here: the eye zig-zags with the music | beats 84, 95, 105, 116 |
| 5.04-6.32 | f126-157 | **A05 Blanka leaps the cage** (P1, f126-146) → **A06 arena aerial clash in light shafts** (P2, f147-167) | beats 126, 137, 147 |
| **ACT 2 CHARGE** | | | |
| 6.32-8.76 | f158-218 | The bass thins. Panel cuts every beat: **A07 Ken handstand flip** (f168) → **A08 Balrog over a downed Ken** (f188) → **A09 psycho-power energy ball** (f209). Her row enters the bottom of the roll window around f150. At **f200 the P1 select cursor** (2 px saffron frame + `P1 · SELECT` tag, Chakra Petch 600, 34 px) appears on her row and **tracks it** as it rises. The other names start dimming (100% → 60% by f232) | bass thins f158, back f178; beats 168-209 |
| 8.76-9.72 | f219-242 | **Fill cuts on the fill hits**: A10 Chun-Li's fireball scream (f219), A11 Ryu vs Blanka cage (f224), A12 Guile glare (f232), A13 Cammy (f238). 5-8 frame shots, with a 2-frame saffron slash-wipe on each | fills f219/224/232/238 |
| **9.72-10.40** | **f243-260** | **THE HOLD.** Bass-out. The roll **decelerates to a stop** (ease-out over f243-252) with her row parked at **y 1536**. All other names fade to 22%. Her name alone (right column only) turns Saffron. The panels merge into **one wide band** with **C00 Ryu's and Ken's fists approaching** in drained near-mono (optical-flow ~33% speed, 143.73 → 143.977). Then **ki charge**: 40 saffron motes spiral into her row, the cursor tag flips to `P1 · LOCKED` at f254 (riser), and the frame pushes in 1.00 → 1.03 | **bass-out f233-253**, riser f254 |
| **ACT 3 SUPER ART** | | | |
| **10.44** | **f261** | **THE POP** (section 6). The fists make contact on this exact frame (src 143.977). Flash, name rip and scale, double shockwave, roll shatter, band slam, sparks, shake, chromatic split. **Colour unlocks inside the band** | **DROP** (+31 dB sub) |
| 10.64-11.04 | f266-276 | **B01** continues: the fist contact ramps 100% → 20% and holds (freeze tail f272-276). Name settled at f272. A small `SUPER ART` tag (Chakra Petch, Ink on Ki White) slides in under the band's lower-left edge f266 and leaves f300 | beat 266 |
| 11.08-14.00 | f277-349 | **The roster fights for her: one hit per beat inside the band**, hard cuts. **B02 Balrog uppercut** (f277) → **B03 Blanka electric dash** (f289) → **B04 red-room backflip (Vega?)** (f300) → **B05 explosion silhouettes** (f310) → **B06 Ken vs Dhalsim punches** (f320) → **B07 aerial flip over the club crowd (Cammy?)** (f330) → **B08 Chun-Li turns** (f340). On every cut: a 2-frame band border flash (Saffron), a 3 px name nudge along the -12° axis, and a 10% rim-glow pulse on the name. **Roto pop-outs:** on B02 (the glove) and B03 (Blanka), the fighter breaks **out of the band edge** for 6-8 frames (matte from Roto). Above and below the band, two thin echo bands (2160x260, tritone, 0.35x speed) scroll the outgoing shot: the "afterimage" of each hit | beats 277-340 |
| **ACT 4 TITLE** | | | |
| 14.00 | f350 | **Collapse**: the band's top and bottom edges close onto the name in 6 frames (expo-in); a 1-frame Ki White slash-line at -12° | beat 350 |
| 14.00-15.20 | f350-379 | **Title card** builds on the beats. The line-up art (`assets_prev/lineup_restored_2160_r470.png`, tritone + saffron rim, bottom-anchored, slow push 1.00 → 1.04 to f450) rises in from below. The **SF logo** (`sf_logo_alpha.png`, mapped to saffron/Ki White gold) lands at f360 (y 700-1150). The name moves from the band position to y 1500-1950 (11-frame ease) and keeps the Ki glow at 40%. **Saffron rule** (420x8) draws L→R f370-378 | beats 360, 370 |
| 15.20-16.10 | f380-402 | `SR. MATCHMOVE ARTIST` rises 24 px and fades in on f380 (Barlow Condensed 600, 96 px, +0.30em, Ki White). `STREET FIGHTER  ·  DNEG` follows on f392 (Barlow Condensed 600, 64 px, +0.30em, Chalk) | beats 380, 392 |
| 16.10-18.00 | f403-449 | **Hold.** Only ambient life: smoke drift on the line-up, 3 saffron embers rising, slow push. Audio fades f425-449; picture holds full until f449 (no fade to black: the last frame is a poster frame) | fade f425-449 |

### 4.1 Edit grid (frame numbers for every cut)
`0, 42, 84, 105, 126, 147, 168, 188, 209, 219, 224, 232, 238, 243, [261 POP], 277, 289, 300, 310, 320, 330, 340, 350 (collapse), 360, 370, 380, 392`
Cut rhythm: 4 beats → 2 beats → 1 beat → half-beat fill → **hold** → 1 beat → title holds. Average shot length is 42 f, then 21, 10, 6; it hits 18 at the hold, 11 in the chain, and 100 for the title. The arc is establish → develop → climax → resolve.

## 5. Colour direction: "KI TRITONE → COLOUR UNLOCK"
song_mood suggested `punjabi-night` / `night-neon` (teal shadows). **Rejected**: teal is the blue cast the client dislikes, and PARALLAX already did cool. The music is D minor, driving and swaggering, so the grade is dark and hot, but warm.

**The idea:** colour is the special effect. Before the drop the film exists as a **two-tone ki world** (Aubergine shadows → Saffron highlights). On the drop, **colour unlocks inside the band only**, so the whole frame visibly levels up when her name lands. In the title, the line-up art returns to tritone with a saffron rim: the world after the hit.

### Palette (hex)
| Name | Hex | Use |
|---|---|---|
| Aubergine Ink | `#14080F` | base black, background, shadows of the tritone (warm purple-black, R > B) |
| Mulberry | `#4A1838` | shadow-mid of the tritone, name drop-shadow, vignette |
| Plum | `#7A2E5C` | mid of the tritone (small areas) |
| **Saffron** | `#FFB12A` | THE accent: highlights of the tritone, cursor, rings, sparks, rule, band border, her row before the pop |
| Ki White | `#FFF3DC` | type (roll, name, title), flash, hottest highlights |
| Chalk | `#D9CFC3` | secondary type (`STREET FIGHTER · DNEG`), dimmed roll |
| Cinnabar | `#FF5A1F` | spark tips only, ≤ 1% of pixels |

### Grades (Colorist owns; all as `.cube` LUTs + an ffmpeg chain, applied per plate in the edit)
1. **TRITONE (`tritone.cube`)**, used for Act 1-2 panels, echo bands and title line-up art. Desaturate to luma (Rec.709 weights), lift and contrast `curves=0/0 0.12/0.06 0.5/0.45 0.85/0.85 1/1`, then gradient-map luma 0 → `#14080F`, 0.25 → `#4A1838`, 0.5 → `#7A2E5C`, 0.78 → `#FFB12A`, 1.0 → `#FFF3DC` (interpolate in OKLab, not sRGB, so the mulberry-to-saffron mid stays vivid and never goes brown-grey). Film grain `noise=alls=7:allf=t`. My board (`lookdev/board.html`, the SVG `#tri` filter) is the starting reference.
2. **DRAIN (f243-260)**: the tritone at 35% chroma (near-mono plum/bone) and -0.3 EV. It makes the colour unlock land harder.
3. **UNLOCK (`band.cube`)**, used for the Act 3 band (B01-B08). Full colour, but designed: contrast up (S-curve), saturation 1.15 on skin/reds/oranges/greens. **Blues are re-hued toward violet-mulberry** (hue +35°, chroma ×0.7), highlights roll off to Ki White, shadows sit on Aubergine. Every band frame must pass **mean R ≥ mean B**. B01, B07 and B08 are blue-lit at source and are the test cases. **Note:** my board's quick band mock went greenish on B01; that is exactly what to avoid (pull green out of the shadows; skin stays warm).
4. **Title**: tritone line-up plus the logo mapped to a saffron→Ki White gradient (not the stock red-orange, which belongs to the trailer/v1), with a 6% bloom on highlights.

**QC (Colorist + QC):** for every output frame, mean B ≤ mean R, and no frame's tritone areas contain chroma outside the palette ramp. Blacks never go below `#14080F` (no pure 0 black except the letterbox-free edges), and nothing clips to pure 255 except the 2-frame flash.

## 6. The special effect: her name's Super Art (f243-f272)
Built as its own sub-composition by **MG2** (section 10), over transparent, 2160x3840, frame-numbered to the master.

**Charge (f243-260)**
- **Cursor lock**: from f200 a saffron 2 px rectangle hugs the right-column cell of her row with 16 px padding; corner ticks are 40 px L-brackets. At f243 the brackets **snap in** from 1.25x to 1.00x (6 f, expo-out). At f254, `P1 · SELECT` swaps to `P1 · LOCKED` (1-frame swap, saffron fill → Ki White fill).
- **Roll stop**: the scroll velocity eases from 19 → 0 px/frame over f243-252, and her row stops at y = 1536. All other names fade to 22%.
- **Ki motes**: 40 particles (6-14 px soft dots, Saffron → Ki White) spiral in on a 2-turn log-spiral from radius 1100 to 0 around her row centre, arriving f258-260. Their trails are 6 frames long, blended additively.
- **Push-in**: whole-frame scale 1.00 → 1.03 (f243-260, ease-in-out).
- **Under it**: C00 (the fists approaching) in the drain grade, centred band y 1300-2200.

**Impact (f261-272)**: every layer is keyed to f261 = 0
| Layer | Spec |
|---|---|
| Flash | Ki White full-frame, screen blend: f261 85%, f262 45%, f263 0% |
| **Name rip & scale** | Her text (right-column cell, Montserrat 44 px cap, Saffron) **cross-morphs** in 2 frames into the hero setting: **SUKANYA** (Barlow Condensed 900 Italic, cap 300 px) over **DILIP DHARIYA** (cap 220 px), centred x 1080, block centre y 1700, line gap 0.86 em. Scale/position f261-267 with `ease-out-expo` and **6% overshoot**, settling at f272, with 12-sample motion blur on the scale. Fill: Ki White. Inner edge glow Saffron (18 px, 80%). Hard offset shadow Mulberry (0, +18 px). A **1-frame saffron outline ghost** at 1.12x on f261. |
| Shockwave ×2 | Ring 1: radial displacement (refraction 24 px) plus a 6 px Ki White ring, radius 0 → 2600 px in 10 f (expo-out), opacity 1 → 0. Ring 2: 3 frames later, 3 px, to 1800 px. Both centred on the name. |
| **Roll shatter** | Every visible roll row (two-column strip) becomes a rigid card that **flies radially away from her row**: velocity 1800-3200 px/s (random per row, seeded), rotation ±6°, fully gone by f273 (opacity 1 → 0, ease-in), with directional motion blur. The crew makes way for her. |
| **Band slam** | A parallelogram 2160+240 px wide, 900 px tall, skew -12°, centred on y 1700, slams in from x +2400 to 0 in **4 frames** (f261-264, expo-out, 3% overshoot). It holds B01 in the **unlock** grade, with a 6 px Saffron border plus a 40 px Saffron outer glow at 50%. The name sits ON the band. |
| Sparks | 300 sparks emitted from the band's left and right contact edges and from the name centre. Each is 2x(12-28) px, Ki White → Saffron → Cinnabar over its life (8-20 f), with gravity 2200 px/s² and drag 0.08. |
| Speed lines | 24 radial lines, 2-6 px, Ki White at 40%, f261-266, converging on the name |
| Shake | Whole frame (not the type layer): offsets 18 / -10 / 5 / -2 px on f261-264 along the -12° axis |
| Chromatic split | f261-263: R/B channel offset 6 / 3 / 1 px, footage layer only, **never on the type** (the name stays crisp) |
| Sub-hold | From f266, a 10% Saffron rim-glow pulse on the name on every beat (f266, 277, 289 ... 340) |

**Restraint:** no lens flare, no "ting", no glitch noise, no 3D spin. The name is never blurred after f267.

## 7. Typography (Google Fonts, TTFs in `shots/sh010/director/v001/fonts/`)
| Role | Font | Size at 4K | Tracking | Colour |
|---|---|---|---|---|
| Roll names | **Montserrat 500**, caps | cap 44 px, row pitch 93 px | +0.02em | Ki White; dim Chalk at 22% when dimmed |
| Roll header | Barlow Condensed 600 | 64 px | 0 | Ki White 85% |
| Hero name (pop + title) | **Barlow Condensed 900 Italic**, caps | SUKANYA cap 300 / DILIP DHARIYA cap 220 (pop); ×0.8 on the title | +0.01em | Ki White + Saffron glow + Mulberry offset shadow |
| `SR. MATCHMOVE ARTIST` | Barlow Condensed 600 | 96 px | +0.30em | Ki White |
| `STREET FIGHTER  ·  DNEG` | Barlow Condensed 600 | 64 px | +0.30em | Chalk |
| HUD (`P1 · SELECT`, `P1 · LOCKED`, `SUPER ART`) | **Chakra Petch 600** | 34 px | +0.12em | Aubergine on a Saffron/Ki White chip |

All type is native DOM/vector at 2160x3840. Never rasterise at 1080 and upscale. The roll text is the same Montserrat at every stage, so the pop's cross-morph is font-continuous until f263.

## 8. Shot list (trailer `source/trailer.mp4`, 1280x720 @ 23.976; active picture `crop=1280:536:0:92`)
In `cues.json`, `f_out` is exclusive; this table shows inclusive frames. Every shot sits inside ONE trailer shot (checked against the librarian's `shots.json` cut list; the ids are in `cues.json` notes). Speeds are 0.94-1.25x, except the deliberate slow-mo (A01 and A07 0.79, A02 0.51, C00 0.34, the B01 ramp). Crop format is `w:h:x:y` in **full-frame** pixels (the y already includes the 92 px letterbox). "Layer": roll_panel = Act 1-2 slash panels (tritone); charge = drained band; super_band = Act 3 band (unlock grade). The frame ranges are master frames.

| ID | Trailer in-out (s) | Master f | Characters | Crop | Notes |
|---|---|---|---|---|---|
| A01 | 38.29-39.62 | 0-41 | Dhalsim, Ken | 960:536:160:92 | lib sf032: Ken knocked down on the white floor, Dhalsim's stance (0.79x) |
| A02 | 141.90-142.76 | 42-83 | aerial fighter (lib sf124: unknown) | 960:536:160:92 | flying kick through arena light shafts, 51% optical-flow slow-mo |
| A03 | 62.00-62.90 | 84-104 | E. Honda | 720:536:300:92 | close-up stare, sauna |
| A04 | 109.45-110.45 | 105-125 | red-jacket fighter (lib sf097: unknown) | 1280:536:0:92 | fights silhouettes in light slats (1.19x) |
| A05 | 112.58-113.40 | 126-146 | Blanka | 960:536:160:92 | leaps over the cage, arms up |
| A06 | 135.90-136.80 | 147-167 | Ken + opponent | 1280:536:0:92 | arena light shafts, aerial clash |
| A07 | 40.92-41.55 | 168-187 | Ken | 960:536:160:92 | handstand flip in shafts |
| A08 | 51.97-52.76 | 188-208 | Balrog, Ken | 1280:536:0:92 | lib sf046: Balrog stands over Ken knocked down, arena wide |
| A09 | 107.00-107.50 | 209-218 | unknown (psycho-power energy ball, lib sf093) | 960:536:160:92 | violet energy ball, in palette |
| A10 | 123.70-123.90 | 219-223 | Chun-Li | 960:536:160:92 | lib sf111: Chun-Li screams in front of a fireball; half-beat flash |
| A11 | 130.30-130.62 | 224-231 | Ryu, Blanka | 960:536:160:92 | cage, purple spark |
| A12 | 95.45-95.70 | 232-237 | Guile | 720:536:280:92 | flat-top glare |
| A13 | 121.30-121.50 | 238-242 | Cammy | 720:536:280:92 | braids, leotard |
| C00 | 143.73-143.977 | 243-260 | Ryu, Ken | 1280:536:0:92 | fists approach at ~33% (optical flow); **frame 143.977 (contact) = master f261** |
| **B01** | 143.977-144.06 | **261-276** | **Ryu, Ken** | 1280:536:0:92 | **the fist contact**; ramp 100 → 20%, freeze tail f272-276 |
| B02 | 50.10-50.65 | 277-288 | Balrog (vs Ken) | 1280:536:0:92 | low-angle uppercut; **roto pop-out of the glove** |
| B03 | 139.75-140.25 | 289-299 | Blanka | 1280:536:0:92 | electric dash; **roto pop-out** |
| B04 | 113.55-114.00 | 300-309 | Vega? (confirm) | 1280:536:0:92 | red-room backflip |
| B05 | 123.00-123.45 | 310-319 | fighters in silhouette | 1280:536:0:92 | explosion firewall (already saffron) |
| B06 | 132.35-132.80 | 320-329 | Ken, Dhalsim | 1280:536:0:92 | punch exchange, crowd |
| B07 | 101.36-101.81 | 330-339 | Cammy? (aerial flip, club) | 1280:536:0:92 | magenta/blue club light → re-hue |
| B08 | 152.00-152.40 | 340-349 | Chun-Li | 1280:536:0:92 | buns, turns to camera; the band collapses at f350 |
| T01 | assets_prev line-up art | 350-449 | full line-up | 2160 wide, bottom-anchored | tritone + saffron rim, push 1.00 → 1.04 |

**Framing rules:** slash panels (2160x1180) take a 960x536 source crop (×2.25). The band (2400x900 visible) takes the full 1280x536 (×1.88), so the band is the sharpest footage in the piece, which is right for the hero. Prep is deblock with the grid realigned (pad 4 rows: `pad=1280:540:0:0,deblock=filter=strong:block=8`, then crop back), then lanczos upscale, then a light `unsharp=5:5:0.4`. Retimes use `minterpolate=fps=75:mi_mode=mci:mc_mode=aobmc:vsbmc=1`, then pick frames. Check every slow-mo for warping on limbs; if it warps, use frame-blend instead.
**Trailer frame rate:** the trailer runs at 23.976 and the master at 25. Editors **conform by frame mapping** (`src_t = src_in + (f - f_in)/25 * speed`), never by `-r` on the whole file, so the C00/B01 contact frame lands on f261.

## 9. Sound plan
- **Music only**: her track, 116.30-134.30 (`audio/bed_client_116.30-134.30.wav` is the reference cut). **No added SFX** (no synthetic ting, no whooshes): the drop *is* the hit, and the picture is cut to it.
- **Edits**: 3-frame (120 ms) fade-in at the head, because 116.30 sits 38 ms after the beat at 116.262 and the attack tail must not click. Fade-out f425-449 (1.0 s, an equal-power curve). The last frame of picture is f449.
- **Creative move (different from PARALLAX's stereo narrowing and v4's untouched silence)**: a **"charge" filter on the music**, f219-260. A low-pass sweep from 20 kHz down to 2.5 kHz (exponential, f219 → f258) plus a 1-2 dB gain dip, then **bypassed instantly at f261**. The track's own bass-out plus our low-pass makes the drop open up to full bandwidth on the pop, in sync with the colour unlock. Picture and sound level up together. This must be subtle: if it reads as an effect, halve it.
- **Master**: `tools/vfx/bin/master_audio.sh mix.wav master.wav youtube` → **-14 LUFS integrated, ≤ -1 dBTP**, then AAC 320 k. Re-measure after AAC and confirm ≤ -1.0 dBTP (the source is -7.9 LUFS and heavily limited, so expect about 6 dB of gain reduction, not compression).
- **Sync check**: on the final file, the 10 ms sub-band transient must fall within ±1 frame of f261.

## 10. BUILD PLAN AND TEAM (for the producer)
Everything is frame-locked to `cues.json` and 2160x3840 at 25 fps. **Parallelise thinking and building, not rendering**: at most 2 heavy jobs at once (HyperFrames 4K renders, minterpolate retimes, rembg). Disk is tight (about 4.8 GB free): **no ProRes 4444 at 4K**. Intermediates are H.264 `-crf 10 -pix_fmt yuv444p` for opaque plates, VP9-alpha `.webm` or short PNG sequences (≤ 30 frames) for alpha, and proxy work at 540x960. Delete scratch after hand-off.

### Team: 15 agents (all can start at T0 except where noted)
| # | Dept / agent | Count | Owns | Writes to | Reads |
|---|---|---|---|---|---|
| 1 | **Shot Librarian** (delivered `shots.json`) | 1 | stays on call: IDs for the unknowns (A02, A04, A09, B04, B07) and alternates if a shot fails | `library/streetfighter-trailer/shots.json` | trailer |
| 2 | **Storyboard / animatic** | 1 | a 540x960 animatic of all 450 frames: real cuts from `cues.json`, grey-box type and FX, the bed on it. **Due T0+35 min.** Every department checks timing against it | `shots/sh010/previs/v001/animatic_540.mp4` | cues.json, selects |
| 3 | **Editor A: Roster** | 1 | plates A01-A13: deblock, crop, retime and conform to exact frame counts | `shots/sh010/edit/v001/plates/A01.mp4`... at 2160x1180 (panel size) + `edl_A.json` | cues.json |
| 4 | **Editor B: Super Art** | 1 | C00, B01-B08: deblock, conform, the **C00/B01 contact-frame alignment to f261** (frame-step proof PNG), slow-mo ramps | `shots/sh010/edit/v001/plates/B01.mp4`... at 2400x900 + `edl_B.json` + `contact_proof.png` | cues.json |
| 5 | **Roll typesetter A: transcription** | 2 (A1 + A2, independent) | transcribe the ~30 rows **above** SAMITH SOUMYANATH from movie.mp4 56.0-63.5 s; each writes its own list, then A1 diffs them and writes the merged, verified list (rows the two disagree on, or cannot read, are dropped) | `shots/sh010/roll/v001/rows_A1.txt`, `rows_A2.txt`, `rows_verified.txt` | movie.mp4, credits.txt |
| 6 | **Roll typesetter B: component** | 1 | the roll as a HyperFrames/HTML sub-comp: Montserrat, 93 px pitch, gutter x 1083, 19 px/frame, ease-to-stop f243-252 with her row at y 1536, dimming, **and per-frame row positions** exported for MG1/MG2 | `shots/sh010/roll/v001/roll.html`, `roll_rows.json` (per frame: each row's y), `roll_check.png` (overlay vs the real 64.0 s frame at matching scale) | rows_verified.txt (uses credits.txt first, appends rows when they arrive) |
| 7 | **Colorist** | 1 | `tritone.cube`, `drain.cube`, `band.cube`, the title look; grade test frames on A01, A08, B01, B07, B08; the R ≥ B QC script; final 4K deliver checks | `shots/sh010/color/v001/*.cube`, `grade_tests.png`, `qc_rgb.py` | plates (the first ones from the editors; can start on director stills) |
| 8 | **MG1: Roster comp** (Acts 1-2) | 1 | slash panels P1/P2 (skew -12°, wipes, 0.6x drift), header, ambient smoke/grain bg, cursor tracking from `roll_rows.json`, the dim ramp, ki motes, push-in | `shots/sh010/mograph/v001/mg1_roster/` (comp HTML) | roll.html, plates A*, tritone.cube |
| 9 | **MG2: Super Art FX** (f243-276) | 1 | everything in section 6: cursor lock, motes, flash, **name rip/scale**, shockwaves, **roll shatter** (rows from `roll_rows.json` at f261), band slam, sparks, speed lines, shake, CA. Alpha sub-comp | `shots/sh010/mograph/v001/mg2_superart/` + proxy `mg2_proxy_540.webm` | roll_rows.json, B01 plate, fonts |
| 10 | **MG3: Band chain** (f261-349) | 1 | the band with B01-B08, beat border flashes, name nudge/pulse, echo bands, `SUPER ART` tag, **roto pop-outs** comped over the band edge | `shots/sh010/mograph/v001/mg3_band/` | plates B*, roto mattes, band.cube |
| 11 | **MG4: Title card** (f350-449) | 1 | collapse, line-up art push, gold-mapped logo, name re-position, rule, lines on beats, embers | `shots/sh010/mograph/v001/mg4_title/` | assets_prev, fonts |
| 12 | **Roto** | 1 | rembg (`u2net_human_seg`) mattes for B02 (glove/arm) and B03 (Blanka), about 12 frames each, temporal-median cleaned; SAM 2 only if rembg fails (heavy slot) | `shots/sh010/roto/v001/B02_matte.webm`, `B03_matte.webm` + over-black/over-white check PNGs | plates B02/B03 |
| 13 | **Sound** | 1 | head fade, charge low-pass f219-260 with bypass at f261, tail fade, master to -14 LUFS / ≤ -1 dBTP, sync proof | `shots/sh010/sound/v001/master.wav`, `sync_proof.png` | bed, cues.json |
| 14 | **Comp lead / mograph lead** | 1 | the master composition: imports MG1-MG4 by frame range, enforces the motion-language spec (2 eases, 11-frame unit, -12° family, one wow), audio, **the only 4K render** | `shots/sh010/comp/v001/master/` → `render/sukanya_v2_4K.mp4` | all of the above |
| 15 | **QC** | 1 | checks each hand-off: frame counts, ±1 f sync on f261 and every cut, R ≥ B, legibility of the roll at phone size (downscale to 1080x1920 and read it), alpha edges over black and white, no black frames, `ffprobe` of the final | `review/qc_*.md` (notes), contact sheets | everything |

The Director (me) reviews the animatic, the MG2 proxy and the comp at 540 proxy, and writes `review/director_v001.md`.

### File interfaces (contracts)
- **Timing**: `cues.json` only. A change to any cut goes through the Director via `make_cues.py`. Nobody edits frame numbers locally.
- **Plates**: `edit/v001/plates/<ID>.mp4`, exactly `f_out - f_in` frames, 25 fps, **ungraded** (deblocked + scaled). The colorist's LUTs are applied **in the comp** (HyperFrames: pre-graded copies `color/v001/plates/<ID>.mp4` made by the colorist with `lut3d`, same names). This lets editors and the colorist work at the same time.
- **Roll**: `roll/v001/roll_rows.json` = `{ "frames": [ {"f":0,"rows":[{"i":0,"y":...},...]}, ...], "her_row_index": N, "pitch":93, "gutter_x":1083 }`. MG1 tracks the cursor from it and MG2 shatters from it at f261.
- **Sub-comps**: each MG agent delivers a self-contained HyperFrames composition sized 2160x3840 with **master frame numbers** (comp starts at its first master frame, as `data-start` / offset), transparent where it doesn't own pixels. Each also delivers a **540x960 proxy render** of its range for review. **No MG agent renders 4K**; only the comp lead does.
- **Fonts/colours**: only from `director/v001/fonts/` and the palette table. Any new hex needs the colorist's sign-off.

### Schedule (IST, from producer spawn at T0 ≈ 16:55 IST)
| IST | Milestone |
|---|---|
| T0 (≈16:55) | spawn all; Editors A/B, Roll A1/A2, Colorist, Storyboard, Sound, MG1-4 (on placeholders) start together |
| +35 min (≈17:30) | animatic; first plates; `rows_verified.txt`; LUT v1; sound master v1 |
| +60 min (≈17:55) | roll.html + roll_rows.json; roto mattes; all plates + graded plates |
| +90 min (≈18:25) | MG1-MG4 540 proxies → **Director review 1** (notes within 15 min) |
| +120 min (≈18:55) | fixes; the comp lead assembles; full 540 proxy of the master → **Director review 2** + QC |
| +135 min (≈19:10) | **4K render** (450 frames; HyperFrames at 4K, estimate 25-40 min on 2 cores) |
| +175 min (≈19:50) | QC on the 4K → `deliver/sukanya_v2_4K.mp4` |

**Heavy-job queue (max 2 at a time):** the minterpolate retimes (Editor B's C00/B01/A02 first) → rembg (Roto) → the proxy renders (one per MG at a time, alternating) → the final 4K render (it runs alone, with nothing else heavy alongside).

## 11. The Short: thumb-stopping moment
**f261-266**: the Ki White flash fading, the band mid-slam with the fist contact in fresh colour, her name at peak overshoot, rings and sparks. The poster/cover frame is **f272** (the name settled on the band, sparks still flying). A second option is **f449** (the title card, clean). The comp lead exports both as 4K PNGs.

## 12. Risks and fallbacks
- **Too few transcribable rows above her row** → start the roll at 70% speed (section 2.2). Never invent names.
- **Optical-flow warps on C00/B01** → use B01 at native speed with a 4-frame freeze on the contact, and start C00 earlier (143.50-143.977) at 50%.
- **A "?" character ID is wrong** → the Shot Librarian's ID wins; the shot stays, because on-screen labels never name characters (we show fights, we don't caption them).
- **The band grade cannot pass R ≥ B on B07/B08** → swap B07 for 146.25-146.80 (Ken vs Dhalsim, warm arena) and B08 for 136.25-136.70 (aerial, warm).
- **The 4K render is slow** → render in two halves (f0-260, f261-449) as one job queue, concatenated frame-exactly.
