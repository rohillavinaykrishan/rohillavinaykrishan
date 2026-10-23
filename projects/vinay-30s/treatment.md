# Treatment: "SPECTRUM"
VINAY KRISHAN ROHILLA · Sr. Matchmove Artist · DNEG · Street Fighter
30.0 s · 2160x3840 · 25 fps · **750 frames (f0-f749)** · ONE deliverable: `deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_30s_4K.mp4`
Written by the Director, 2026-10-24, 00:40-01:15 IST; finalised 02:45 IST after a container restart.

Director data (inputs, not reports): `shots/sh010/director/v001/`
- **`cues.json`**: the single source of truth for timing: music segments, beat grids (frames), events, every shot (library id, trailer in/out, speed, crop, characters, grade, hue), the 8 wall tiles, the 4K layout boxes, palette and fonts. **If this document and `cues.json` disagree, `cues.json` wins.**
- `make_cues.py`: regenerates `cues.json` (edit its tables; never hand-edit the JSON).
- `audio/make_bed.py` → `audio/bed_vinay30_v001.wav` (the 30.000 s bed, 48 kHz/24-bit) + `audio/bed_segments.json`; `audio/mood.json` (song_mood); Whisper VAD-off checks: `audio/whisper_vadoff.py`, `audio/whisper_vadoff_strict.py`, `audio/whisper_bed_*.json`, `audio/raw_trailer_*.json`.
- `fonts/` Unbounded-900, Unbounded-500, SpaceMono-700 (TTFs from the Google Fonts CSS API).
- `sheets/candidates.jpg` (every library still considered, labelled).

---

## 1. Big idea and logline
**Logline:** Eight world warriors, eight colours of light; when they collide, they fold into one white-hot name: VINAY KRISHAN ROHILLA.

**Meaning.** A matchmove artist is the person every shot passes through: each fighter's plate, each camera, gets solved by the same hands, and nobody sees the seams. So the film is built as a **spectrum**: every fighter owns one colour (the client reference is exactly this, character-coded colour energy on black), and white light is what you get when all colours add up. His name is that white light. No trackers, no point clouds, no roll: the craft is in the *meaning*, not in a breakdown we have already done three times.

**Why it differs from all five earlier pieces**
| Earlier | What it did | SPECTRUM instead |
|---|---|---|
| v1/v2 | hard-cut 9:16 crops + freeze zoom | no 7x vertical crops; widescreen windows inside a designed vertical frame; one silent beat instead of a freeze |
| v3 THE SOLVE | red/gold flat roll + 2D trackers | no roll, no trackers; 8-hue roster then white |
| v4 GROUND TRUTH | COLMAP solve, 3D monument, sand/pink | flat graphic light, no 3D, no breakdown |
| PARALLAX | silver B&W + lime, floating 3D names | full spectrum on ink black, flat type |
| SUPER ART | plum/saffron tritone, roll, -12° band, Super Art pop | 8 separate duotones, ink-brush wipes (organic, horizontal), the name forms from 8 coloured copies collapsing into one; ends on a **character-select roster wall**, not line-up art |

New to this series: **ten named fighters** (Ryu, Ken, Dhalsim, Blanka, Guile, Chun-Li, M. Bison, E. Honda, Balrog, Cammy), a wide geometric name face (Unbounded 900), a **real silence** before the hit, and an ending that lands on the trailer's own title-card stinger.

## 2. What the material says
### 2.1 Music decision: a 4-part trailer bed, 3 splices (`audio/make_bed.py`)
| Seg | Trailer src (s) | Master (s / f) | What it is | Why |
|---|---|---|---|---|
| S1 | 63.875-73.350 | 0.000-9.475 / f0-236 | bathhouse fight cue, instrumental, 117.5 BPM (12.77 f/beat), rising | a stalking groove for the roster call; the cleanest instrumental stretch in the trailer |
| S2 | 122.825-127.620 | 9.475-14.270 / f237-356 | explosion hit, then the sung hook **"I'm a street fighter"** (src 126.16-127.58 → **f320-356**) | the one lyric that says it; it becomes the charge into his name |
| S3 | 104.880-109.995 | 14.270-19.385 / f357-484 | **0.33 s of silence (-43 dBFS) then the trailer's biggest hit (src 105.21)**, then a 136 BPM drive (11.03 f/beat) | the silence + hit is the hero beat: **HIT = f365** (bed onset measured at 14.594 s) |
| S4 | 145.925-156.525 | 19.385-30.000 / f485-749 | chant section (172.3 BPM, 8.7 f/beat), into the **SF title-card stinger at src 153.97 → f686** | the ending card lands on the film's own title hit |

- Splices: S1→S2 cuts on S1's beat and drops into S2's explosion hit (+15 dB, reads as a designed slam-in); S2→S3 cuts from the end of the sung word "fighter" straight into the trailer's own silence (a classic trailer stop); S3→S4 cuts on a beat, levels match (-18.4 / -15.5 dB). 6 ms equal-power crossfades, 4 ms head fade, 0.6 s tail fade (f735-749).
- song_mood on the bed: 172.3 BPM (chant half), D minor, "intense, swagger", suggests `punjabi-night` teal shadows. **Rejected** as a grade (teal = the blue cast the client dislikes, and it's a single look). The music says *swagger and rising heat*; the lyric says *identity* ("I'm a street fighter"). That is a colour-identity film, see section 5.
- **Dialogue check, Whisper VAD OFF** (faster-whisper, `vad_filter=False`):
  - small, default thresholds: **0 segments**.
  - small, `no_speech_threshold=None`: one low-confidence hit, "My business that's a" at 29.2-29.98 (first word p=0.06), in the title stinger under the tail fade.
  - medium, `no_speech_threshold=None`: **"I'm a street fighter"** at 12.76 (the sung hook, expected and wanted), a repeat of it at 15.38 (a hallucination over the hit: no vocal there, the trailer's own map has no voice at 104.9-110.2), and "My business is a Ferrari" at 19.46-20.94 (src 146.0-147.5, inside the librarian's **sung chant** span 144.0-153.92; "Ferrari" p=0.01).
  - **Resolved (raw-trailer cross-check, medium, VAD off):** src 144.0-149.0 alone gives "My, my business is a priority" with "business" at src 146.18: the same words at the same place as in the bed, inside the librarian's sung chant span, so it is a **rap/chant lyric in the music cue** (allowed). Src 153.5-156.8 alone gives only "Thank you for watching!" (no_speech 0.91, first word p=0.00: the classic Whisper hallucination on music) and no "my business", so the bed's 29.2 s hit (p=0.06) is a hallucination. The real spoken line "You did that to your face" starts at src 156.69, 0.165 s after the bed ends (156.525) and under the tail fade. **Verdict: the bed contains no spoken dialogue.** Files: `audio/raw_trailer_1440.json`, `audio/raw_trailer_1535.json`.

### 2.2 The footage
The trailer is graded all over the map (blue alleys, magenta clubs, amber arenas). The answer here is not one grade for everything but **one colour per fighter** in Act 1 (duotones remove the mess and make it a system), then **true colour** only after the roster collides (Act 2 onward), so colour itself tells the story. All framings are widescreen windows at ≤2.25x scale (crisp), never vertical 7x crops. Tiles at the end are *downscaled* crops (600x536 → 482x430), the sharpest image in the piece.

## 3. Visual world and motion language
- **World:** ink-black stage, light as the only material. Each fighter enters as a colour of light; brush energy (SF-logo brush strokes) carries the transitions.
- **Personality:** **Energetic** (kinetic-sharp) Acts 1-2; **Premium** holds after the hit. Only two eases: entrances `cubic-bezier(0.16,1,0.3,1)` (ease-out-expo), exits `cubic-bezier(0.7,0,0.84,0)`. Linear only for ambient drift.
- **Base unit:** the beat of the section (12.77 f in Act 1, 17.4 f in Act 2, 11.03 f in Act 3, 8.7/17.4 f in Act 4). Enters = half a beat; micro = 3 f. Overshoot only on the name strike (4%) and the logo slam (3%).
- **Transition family:** hard cuts on beats, plus **ink-brush wipes**: a horizontal dry-brush matte sweeping L→R in 6 frames (a new hue arrives on the leading edge as a 40 px glowing fringe). No slashes, dissolves, spins, glitches, or 3D.
- **Hierarchy:** Act 1 hero = the fighter (portrait + colour), support = giant outline name; Act 2 hero = the clash footage; f357-484 hero = HIS NAME; Act 4 hero = his name, support = the roster wall + logo. **One wow moment: f365.** Second, smaller peak: f686 (logo + roster unlock), which must not outshine f365.
- **Depth:** bg = ink + slow colour plumes and dust (0.2x), mid = footage window / tiles (0.6x), fg = type, rays, sparks (1.0x).
- **Safe areas (2160x3840):** no critical type above y 420 or below y 3140. Name block y 1150-1950, always.

## 4. Timeline (25 fps; f = master frame; exact cuts and src in `cues.json`)
| t (s) | frames | Picture | Music |
|---|---|---|---|
| **COLD OPEN** | | | |
| 0.00-0.76 | f0-18 | Ink black. A 2 px White Hot hairline draws L→R across y 1048 (top edge of the window to come), f0-12; Space Mono label `STREET FIGHTER  ·  DNEG` (34 px, +0.25em, Bone 70%) fades on above it at f6. Faint 8-colour dust motes drift in from the frame edges | S1 starts on its downbeat |
| **ACT 1 ROSTER: eight colours** | | | |
| 0.76-8.92 | f19-222 | **Eight fighters, one per 2 beats, each in its own duotone** (ink → hue → white), in the Act-1 window (2160x904, y 1048-1952). R1 **Ryu** (Crimson) f19 → R2 **Ken** (Orange) f46 → R3 **Dhalsim** (Amber) f71 → R4 **Blanka** (Lime) f96 → R5 **Guile** (Teal) f121 → R6 **Chun-Li** (Blue) f145 → R7 **M. Bison** (Violet) f171 → R8 **E. Honda** (Magenta) f197. The hues walk the colour wheel in order. Each arrival: an ink-brush wipe in that hue (6 f), and above the window the fighter's name in **Unbounded 900 outline** (cap 420 px, 6 px stroke in the hue, 12% fill) slides 80 px L→R over its slot (linear) and exits with the next wipe; below the window a Space Mono tag `01 / 08` … `08 / 08` (34 px, Bone). Behind everything, a soft plume of the current hue breathes from the frame edges (≤ 25% opacity), so the whole frame takes the fighter's colour | beats f19, 46, 71, 96, 121, 145, 171, 197 (every 2nd S1 beat) |
| 8.92-9.47 | f223-236 | **Spectrum shutter:** the window splits into 8 horizontal slivers (113 px each), each holding the last frame of R1-R8 in its hue, top to bottom in wheel order; they strobe on the beat f223 and tighten towards the centre line on f236 (ease-in-expo) | beat f223, f236 |
| **ACT 2 CLASH: the colours collide** | | | |
| 9.48-10.48 | f237-262 | **Colour breaks into TRUE COLOUR** on the explosion hit: the window opens taller (2160x1206, y 897-2103, 3-frame expo slam). C1 silhouettes against an explosion (0.7x). The 8 slivers burst outwards as 8 coloured light-streaks that orbit the window edges | **S2 entry hit f237** |
| 10.52-13.40 | f263-335 | Fights on the 86-BPM beats, hard cuts: C2 **Balrog** over a downed **Ken** (f263) → C3 **Ken** squares up to **Dhalsim** (f280) → C4 **Ken & Ryu** side by side (f298) → C5 **Ken's** jump kick, arena wide (f316). The orbiting streaks speed up each cut | beats f263, 280, 298, 316 |
| 13.44-14.24 | f336-356 | **The charge, under "I'm a street fighter" (f320-356).** C6 **Dhalsim** lunges at camera, ramping 1.0 → 0.2x and draining to near-mono by f356. The 8 streaks spiral in (2 turns, log-spiral) towards the name centre (x 1080, y 1550), lengthening, hues separating like a prism. Whole-frame push 1.00 → 1.04 | sung hook f320-356 |
| **SILENCE** | | | |
| 14.28-14.56 | **f357-364** | **Hard cut to ink.** Nothing moves except one White Hot point (24 px core, 8-colour fringe) at (1080, 1550), breathing 1.0 → 1.15. 8 frames of true stillness: the only still moment in the film | -43 dBFS silence |
| **THE STRIKE** | | | |
| **14.60** | **f365** | **SPECTRUM STRIKE** (section 6): the point detonates; 8 hue rays; the name forms from 8 coloured copies collapsing into one White Hot name; the Act-3 window slams open below (y 2280-3184) on **H0: Balrog's glove landing on Ken**, contact frame = f365, then 0.3x slow-mo | **THE HIT f365** |
| 14.64-15.44 | f366-386 | Name settles (f374), rays fade (to f380), spectral rim cools to a thin warm gold glow. Window keeps H0 slow-mo | beat f376 |
| 15.48-19.36 | f387-484 | **The roster fights for the name**, one hit per 136-BPM beat inside the lower window, hard cuts: F1 spin kick (f387) → F2 **Blanka** swats (f398) → F3 **Cammy** fires (f409) → F4 **Chun-Li** slash (f420) → F5 **Blanka** leaps (f430) → F6 **Cammy** strides (f441) → F7 handstand in light shafts (f451) → F8 **Ken & Ryu** back to back (f463) → F9 fighter down, arena (f474). On every cut, the window's 4 px border flashes the next fighter hue (2 f) and the name's rim pulses that hue at 30% (4 f). **Role line in on f387**: `SR. MATCHMOVE ARTIST` (Unbounded 500, 92 px, +0.18em, White Hot) rises 24 px under the name; a 520x6 Champion Gold rule draws from centre outwards on f398 | beats f376-474 |
| **ACT 4 ROSTER WALL + TITLE** | | | |
| 19.40-20.08 | f485-502 | **The window shatters into the roster wall:** it splits along the tile grid (2 rows x 4) and the pieces snap into the 8 tile rects (6 f expo). `STREET FIGHTER  ·  DNEG` (Unbounded 500, 64 px, +0.30em, Bone) joins the role line | S4 splice f485 |
| 19.76-25.32 | f494-632 | **Tiles light up one per 2 chant beats**, in wheel order, each with a brush wipe in its hue: T1 **Ryu** f494, T2 **Ken** f512, T3 **Dhalsim** f529, T4 **Blanka** f547 (row 1), T5 **Guile** f564, T6 **Chun-Li** f582, T7 **M. Bison** f599, T8 **E. Honda** f616 (row 2). Each tile plays 40 f at 0.4x in its duotone, then holds its last frame. Tile frame: 3 px hue border, Space Mono name tag in the hue under the lower-left corner (28 px) | chant beats |
| 25.36-27.40 | f634-685 | Breath: name glow breathes once (f634-669); a single White Hot light sweep crosses the name L→R (f651-669); dust drifts | |
| **27.44** | **f686** | **TITLE STINGER:** SF logo (`assets_prev/sf_logo_alpha.png`, original colours kept, it is the brand) slams into the logo box (y 420-1020) from 1.12x to 1.0 in 4 f (3% overshoot), White Hot flash 2 f (40% then 15%). **All 8 tiles unlock from duotone to true colour in the same frame** and their borders blend to Champion Gold: the roster, in full colour, under his name | **SF title hit f686** |
| 27.48-30.00 | f687-749 | **Hold.** Final card: logo / name / role / `STREET FIGHTER · DNEG` / roster wall. Only ambient life (dust, 0.5% push). Audio fades f735-749; picture holds full to f749 (last frame = poster frame, no fade to black) | tail fade |

### 4.1 Edit grid (every cut, master frames)
`0, 19, 46, 71, 96, 121, 145, 171, 197, 223 (shutter), 237, 263, 280, 298, 316, 336, 357 (ink), [365 STRIKE], 387, 398, 409, 420, 430, 441, 451, 463, 474, 485 (wall), tiles 494/512/529/547/564/582/599/616, [686 LOGO]`
Average shot length: 25 f (Act 1) → 18 f (Act 2) → 8 f of silence → 22 f hold → 11 f (flurry) → 265 f final card. Establish → develop → climax → resolve.

## 5. Colour direction: "EIGHT DUOTONES → WHITE LIGHT"
**Idea:** colour is the story. Act 1, each fighter is a single hue (identity); Act 2, the hues collide into true colour (conflict); the silence is colourless; his name is white light (all hues added), carrying a spectral rim only while it forms; the end card unlocks the roster wall to true colour under his name on the logo hit.

### Palette (hex)
| Name | Hex | Use |
|---|---|---|
| Ink | `#07060A` | base black, duotone shadows (never pure #000) |
| Ink Raised | `#13111A` | tile backs, window letterbox, vignette |
| Smoke | `#2B2632` | hairlines, dim outlines |
| **White Hot** | `#FFF8EC` | HIS NAME, flashes, the light point |
| Bone | `#E6DED2` | secondary type (`STREET FIGHTER · DNEG`, tags) |
| **Champion Gold** | `#FFC94D` | the name's settled glow, the rule, final tile borders |
| Gold Deep | `#C7851E` | glow falloff, name keyline shadow |
| Ryu: Hadou Crimson | `#E3203A` | R1/T1 |
| Ken: Shoryu Orange | `#FF5E1A` | R2/T2 |
| Dhalsim: Yoga Amber | `#FFA21C` | R3/T3 |
| Blanka: Volt Lime | `#9BEA2E` | R4/T4 |
| Guile: Sonic Teal | `#17C9A6` | R5/T5 |
| Chun-Li: Kikoken Blue | `#2F6DFF` | R6/T6 |
| M. Bison: Psycho Violet | `#8B3DFF` | R7/T7 |
| E. Honda: Sumo Magenta | `#FF2D8F` | R8/T8 |
The fighter hues appear **one at a time** (Act 1, tiles' arrival) and all together only in the strike rays, the orbiting streaks and the final wall. Never as a rainbow gradient.

### Grades (Colorist owns: `.cube` LUTs + ffmpeg chains, pre-graded plates in `color/v001/plates/`)
1. **DUO-<fighter>.cube** x8 (Act 1 R1-R8, Act 4 tiles before f686): luma (Rec.709) → gradient map 0.00 `#07060A`, 0.28 hue at 30% lightness, 0.60 hue, 0.86 hue mixed 45% with `#FFF8EC`, 1.00 `#FFF8EC`, interpolated in **OKLab** (no muddy midpoints). Pre-curve `curves=0/0 0.1/0.04 0.5/0.48 0.9/0.92 1/1` so faces keep shape. Grain `noise=alls=6:allf=t`.
2. **TRUE.cube** (Act 2 C1-C5, Act 3 H0/F1-F9, tiles after f686): rich, contrasty, warm: S-curve, saturation 1.12 on skin/reds/oranges/greens, blues -15% chroma and pulled 10° towards violet, shadows to Ink, highlights roll to White Hot. Per-frame **mean R ≥ mean B** (F3 Cammy night, F6 neon street and C1 are the test frames).
3. **DRAIN** (C6, f336-356): TRUE ramped to 15% chroma and -0.3 EV by f356 so the silence lands on colourless.
4. **QC rule:** every frame mean R ≥ mean B, **except the designed blue/violet roster beats R5-R7 (f121-196)** and the single tiles T5-T7 (local only; the whole frame passes there). Nothing clips to 255 except the 2-frame flashes; no level below `#07060A`.

## 6. The hero name effect: SPECTRUM STRIKE (f336-f386, peak f365)
Built as its own sub-comp by **MG2**, 2160x3840, transparent, master frame numbers. Name centre (1080, 1550). Name set: **VINAY / KRISHAN / ROHILLA**, Unbounded 900, caps, three lines centred, cap height 230 px, line pitch 270 px, tracking +0.02em (KRISHAN/ROHILLA ≈ 1850 px wide: inside 2160 with 155 px margins; MG2 checks the real width and scales all three lines together to max 1880 px).

**Charge (f336-356):** 8 hue streaks (6-14 px cores, additive, 10-frame trails) on 2-turn log-spirals from r = 1300 to r = 40 around (1080, 1550), arriving f356; push-in 1.00 → 1.04 on the whole frame.
**Silence (f357-364):** ink; the White Hot point (24 px core + 80 px soft halo, an 8-hue fringe 6 px wide rotating 15°/f); scale 1.0 → 1.15. Nothing else.
**Strike (f365 = 0):**
| Layer | Spec |
|---|---|
| Flash | White Hot full-frame, screen: f365 80%, f366 35%, f367 0% |
| **Hue rays** | 8 rays from the centre at 22.5° + k·45°, one per fighter hue (wheel order clockwise from 12 o'clock, Ryu first), 18 px core + 120 px glow, length 0 → 2600 px in 6 f (expo-out), then opacity 1 → 0 by f380 |
| **Name forms from 8 copies** | The name is drawn 9 times: 8 coloured copies (one per hue, additive, 85%) offset outward along their own ray direction by 140 px at f365 and collapsing to 0 px by f373 (expo-out); plus the White Hot master copy, scale 1.35 → 1.00 over f365-370 (expo-out) with a 4% undershoot settling at f374. Where the 8 copies overlap they add to white: the name literally forms out of the roster's light. 8-sample motion blur on the copies only |
| Spectral rim → gold | From f373 the copies leave a 5 px outer rim with a hue gradient around the letters; it cools to a **Champion Gold glow** (outer 36 px, 45%) + Gold Deep keyline (2 px, 0, +6 px) by f386, and stays gold to the end |
| Shockwave | One ring, 4 px White Hot + refraction 18 px on the layers below, radius 0 → 2400 in 10 f, opacity 1 → 0 |
| Window slam | The Act-3 window (y 2280-3184) opens from a 0 px line to full height in 3 f (expo-out) on f365, H0 glove contact on that frame, 0.3x after |
| Sparks | 220 sparks from the 8 ray roots, each tinted its ray's hue → White Hot, life 8-20 f, gravity 1800 px/s², drag 0.08 |
| Shake | Footage + rays only, not the type: 14 / -8 / 4 / -2 px on f365-368 |
**Restraint:** no chromatic RGB split, no lens flare, no 3D spin, no glitch. The name is never blurred after f370. After f386 the only motion on the name is the beat rim pulse (30%, 4 f) and one light sweep at f651.

## 7. Typography (Google Fonts, TTFs in `director/v001/fonts/`)
| Role | Font | Size at 4K | Tracking | Colour |
|---|---|---|---|---|
| HIS NAME | **Unbounded 900**, caps | cap 230 px, pitch 270 px, 3 lines | +0.02em | White Hot, Champion Gold glow, Gold Deep keyline |
| `SR. MATCHMOVE ARTIST` | Unbounded 500 | 92 px | +0.18em | White Hot |
| `STREET FIGHTER  ·  DNEG` | Unbounded 500 | 64 px | +0.30em | Bone |
| Act 1 fighter names | Unbounded 900 outline | cap 420 px, 6 px stroke | +0.04em | fighter hue, 12% fill |
| HUD / tags (`01 / 08`, tile names, cold-open label) | **Space Mono 700** | 28-34 px | +0.20em | Bone / fighter hue |
All type native vector at 2160x3840 (HTML/SVG). Never rasterise at 1080 and upscale. Fighter names are printed only for the 10 characters the librarian names with certainty; "unknown" shots carry no caption.

## 8. Shot list (`source/trailer.mp4`, 1280x720 @ 23.976; active `crop=1280:536:0:92`; library ids from `library/streetfighter-trailer/shots.json`)
`f_out` exclusive. Crop = `w:h:x:y` in full-frame px. Conform by frame mapping `src_t = src_in + (f - f_in)/25 * speed`, never `-r`.
| ID | Lib | Master f | Trailer src (s) | Speed | Crop | Characters | Grade |
|---|---|---|---|---|---|---|---|
| R1 | sf125 | 19-46 | 142.80-143.70 | 0.833 | 1280:536:0:92 | Ryu | DUO Ryu |
| R2 | sf117 | 46-71 | 133.25-134.25 | 1.0 | 1280:536:0:92 | Ken | DUO Ken |
| R3 | sf032 | 71-96 | 38.30-39.30 | 1.0 | 1280:536:0:92 | Dhalsim | DUO Dhalsim |
| R4 | sf100 | 96-121 | 112.58-113.48 | 0.9 | 1280:536:0:92 | Blanka | DUO Blanka |
| R5 | sf082 | 121-145 | 95.02-95.93 | 0.95 | 1280:536:0:92 | Guile | DUO Guile |
| R6 | sf135 | 145-171 | 151.90-152.94 | 1.0 | 1280:536:0:92 | Chun-Li | DUO Chun-Li |
| R7 | sf107 | 171-197 | 119.60-120.28 | 0.65 (frame-blend) | 1280:536:0:92 | M. Bison | DUO Bison |
| R8 | sf053 | 197-223 | 62.00-62.99 | 0.95 | 1280:536:0:92 | E. Honda | DUO Honda |
| C1 | sf110 | 237-263 | 122.93-123.66 | 0.70 | 960:536:262:92 | silhouettes | TRUE |
| C2 | sf046 | 263-280 | 52.00-52.68 | 1.0 | 960:536:76:92 | Balrog, Ken | TRUE |
| C3 | sf116 | 280-298 | 131.90-132.62 | 1.0 | 960:536:90:92 | Ken, Dhalsim | TRUE |
| C4 | sf121 | 298-316 | 138.40-139.12 | 1.0 | 960:536:314:92 | Ken, Ryu | TRUE |
| C5 | sf119 | 316-336 | 135.90-136.70 | 1.0 | 960:536:82:92 | Ken | TRUE |
| C6 | sf033 | 336-357 | 39.65-40.15 | ramp 1.0→0.2 | 960:536:80:92 | Dhalsim | TRUE→DRAIN |
| **H0** | **sf045** | **365-387** | **~50.75 (contact) +0.3x** | 0.30 | 1280:536:0:92 | **Balrog, Ken** | TRUE |
| F1 | sf130 | 387-398 | 146.15-146.59 | 1.0 | 1280:536:0:92 | (red spin kick) | TRUE |
| F2 | sf128 | 398-409 | 144.86-145.30 | 1.0 | 1280:536:0:92 | Blanka | TRUE |
| F3 | sf109 | 409-420 | 121.40-121.84 | 1.0 | 1280:536:0:92 | Cammy | TRUE |
| F4 | sf095 | 420-430 | 108.16-108.56 | 1.0 | 1280:536:0:92 | Chun-Li | TRUE |
| F5 | sf122 | 430-441 | 139.76-140.20 | 1.0 | 1280:536:0:92 | Blanka | TRUE |
| F6 | sf084 | 441-451 | 97.40-97.80 | 1.0 | 1280:536:0:92 | Cammy | TRUE |
| F7 | sf131 | 451-463 | 147.00-147.48 | 1.0 | 1280:536:0:92 | (handstand) | TRUE |
| F8 | sf120 | 463-474 | 137.30-137.74 | 1.0 | 1280:536:0:92 | Ken, Ryu | TRUE |
| F9 | sf123 | 474-485 | 140.80-141.24 | 1.0 | 1280:536:0:92 | (fighter down) | TRUE |
| T1-T8 | sf125, sf031, sf032, sf100, sf082, sf135, sf107, sf053 | arrive 494…616, freeze +40 f | see `cues.json.tiles` | 0.4 | 600:536:x:92 | Ryu, Ken, Dhalsim, Blanka, Guile, Chun-Li, M. Bison, E. Honda | DUO → TRUE at f686 |
| Logo | `assets_prev/sf_logo_alpha.png` | 686-749 | – | – | logo box 380,420 1400x600 | – | original |

**Framing/prep:** windows: Act 1/3 = full 1280x536 → 2160x904 (x1.69); Act 2 = 960x536 → 2160x1206 (x2.25). Deblock with the grid realigned (`crop=1280:536:0:92,pad=1280:544:0:4,deblock=filter=strong:block=8,crop=1280:536:0:4`), lanczos, `unsharp=5:5:0.4`. Slow-mo: `minterpolate=fps=75:mi_mode=mci:mc_mode=aobmc:vsbmc=1` then pick frames; if limbs warp, frame-blend (R7 is frame-blend from the start). **H0's src_in is a placeholder**: the editor frame-steps sf045 (50.05-51.97) for the first frame the glove touches the face and sets that frame = f365 (`H0_contact_proof.png`). E. Honda (sf053) and others carry dialogue in the trailer audio: irrelevant, we never use plate audio.

## 9. Sound plan
- **Music only**: `audio/bed_vinay30_v001.wav` (built by `audio/make_bed.py`; segments in section 2.1). **No added SFX**: the trailer's own hit is the strike; the silence is real.
- Sound polishes, never re-times: splice crossfades may be tuned ±10 ms, but the **hit onset must stay at 14.594 s ±20 ms (f365)** and S4's title hit at f686 ±1 f.
- **One creative move:** none on the hit; instead **keep the silence honest**: no reverb tail, no riser into it. If the S2→S3 cut leaves any click, a 3 ms fade on S2's last word only.
- **Whisper re-check (VAD OFF) on the mastered file**, both `whisper_vadoff.py` (small) and `whisper_vadoff_strict.py ... medium`. Expected/allowed text: "I'm a street fighter" (~12.8 s, sung), "my business..." (~19.5 s, chant lyric) and hallucinations on music ("Thank you for watching", repeats over the hit). Any *new* phrase is a fail: report it with times to the Director. Never let the tail extend past src 156.525 (spoken line at 156.69).
- **Master**: `tools/vfx/bin/master_audio.sh mix.wav master.wav youtube` → **-14 LUFS integrated, ≤ -1 dBTP after AAC 320k** (re-measure after encode).
- **Sync proof**: on the final file, the hit transient within ±1 frame of f365, the title hit within ±1 frame of f686.

## 10. BUILD PLAN AND TEAM (for the producer)
Everything is frame-locked to `cues.json`, 2160x3840 @ 25 fps. **Parallelise thinking and building, not rendering**: ≤ 2 heavy jobs at once (HyperFrames renders, minterpolate, upscales); **the comp lead is the only 4K renderer**. Disk ≈ 11 GB free: no ProRes 4444 at 4K; opaque intermediates H.264 `-crf 10 -pix_fmt yuv444p` (proxy/review: yuv420p), alpha as VP9-alpha `.webm` or ≤ 30-frame PNG runs; delete scratch at hand-off. Proxy work at 540x960.

### Team: 9 agents (all start at T0)
| # | Agent | Owns | Writes to | Reads |
|---|---|---|---|---|
| 1 | **Editor** | all plates: R1-R8, C1-C6, H0, F1-F9 (24) + tiles T1-T8: deblock, crop, scale to window size, retime, conform to exact frame counts; **H0 contact proof**; the C6 ramp | `shots/sh010/edit/v001/plates/<ID>.mp4` (Act 1/3 2160x904, Act 2 2160x1206, tiles 482x430, ungraded) + `H0_contact_proof.png` + `edl.json` | cues.json, trailer |
| 2 | **Colorist** | 8 DUO LUTs, TRUE, DRAIN; grades the plates (lut3d) as soon as each lands; `qc_rgb.py` (R ≥ B with the R5-R7 exception list); grade test sheet | `shots/sh010/color/v001/{duo_*.cube,true.cube,drain.cube}`, `color/v001/plates/<ID>.mp4` (same names), `grade_tests.png` | plates, palette |
| 3 | **FX Elements** (shared kit, keeps all MGs consistent) | ink-brush wipe mattes (3 variants, 6 f, L→R, 2160 wide), colour plume bg (8 hue versions, looping 4 s), dust motes, spark sprite, the light-point sprite with 8-hue fringe; JS helpers for eases/beat lookup | `shots/sh010/mograph/v001/kit/` (webm-alpha/PNG + `kit.js`) | palette, cues.json |
| 4 | **MG1: Roster + Clash** (f0-356) | cold open, Act 1 window/outline names/tags/plumes/brush wipes, spectrum shutter, Act 2 window slam, orbiting streaks, charge spirals (hands spiral endpoints to MG2) | `mograph/v001/mg1_roster/` (HyperFrames HTML) + `mg1_proxy_540.mp4` | kit, graded plates, fonts |
| 5 | **MG2: Spectrum Strike** (f336-386) | section 6 in full: spirals' landing, silence point, flash, rays, 8-copy name collapse, rim → gold, shockwave, sparks, window slam, shake; **owns the name's final geometry** (exports `name_layout.json`: line boxes at 4K) | `mograph/v001/mg2_strike/` + `mg2_proxy_540.webm` + `name_layout.json` | kit, fonts, H0 plate |
| 6 | **MG3: Flurry + Wall + Title** (f387-749) | Act 3 window cuts with hue border flashes, rim pulses, role line + rule, wall shatter, tiles + tags + arrivals, light sweep, logo slam, tile unlock (DUO → TRUE crossfade 1 f), final hold | `mograph/v001/mg3_wall/` + `mg3_proxy_540.mp4` | kit, name_layout.json, graded plates + tiles (both DUO and TRUE versions), logo |
| 7 | **Sound** | section 9: polish, Whisper re-checks (VAD OFF), master -14 LUFS / ≤ -1 dBTP, sync proof | `shots/sh010/sound/v001/master.wav`, `whisper_master_vadoff.json`, `sync_proof.png` | bed, cues.json |
| 8 | **Comp lead** | master HyperFrames comp importing MG1-3 by frame range + audio; enforces the motion spec (2 eases, brush family, one wow); 540 proxy of the master; **the only 4K render**; poster frames f374 + f749 as 4K PNGs | `shots/sh010/comp/v001/` → `render/vinay30_4K.mp4` → `deliver/…_30s_4K.mp4` | everything |
| 9 | **QC + animatic** | at T0: a 540x960 **animatic** from cues.json (library stills in the windows, grey-box type, the bed) due T0+20; then checks every hand-off: frame counts, cut sync ±1 f, f365/f686 sync, R ≥ B, phone legibility (1080x1920 downscale), alpha edges over black/white, no black frames except f357-364 ink (which must be `#07060A`, not 0), final ffprobe (2160x3840, 25 fps, 750 frames, yuv420p, AAC) | `shots/sh010/qc/v001/animatic_540.mp4`, `review/qc_*.md`, contact sheets | everything |
The Director reviews the animatic, MG2 proxy and the master proxy, and writes `review/director_v001.md`.

### File interfaces (contracts)
- **Timing:** `cues.json` only; changes go through the Director (`make_cues.py`). Nobody hard-codes a frame that is in cues.json; read it.
- **Plates:** `edit/v001/plates/<ID>.mp4` exactly `f_out - f_in` frames (tiles: 40 frames, MG3 freezes the last), 25 fps, ungraded. Graded twins at `color/v001/plates/<ID>.mp4` (tiles: `<ID>_duo.mp4` and `<ID>_true.mp4`).
- **Kit:** `mograph/v001/kit/kit.js` exports `ease.out`, `ease.in`, `beat(section, n)`, palette constants loaded from cues.json; MGs use only kit assets for wipes/plumes/sparks.
- **Name geometry:** MG2's `name_layout.json` is the only name layout; MG3 renders the same boxes (no re-typesetting).
- **Sub-comps:** each MG delivers a self-contained 2160x3840 HyperFrames comp in master frame numbers, transparent where it doesn't own pixels, plus a 540x960 proxy. **No MG renders at 4K.**
- **Fonts/colours:** only `director/v001/fonts/` and section 5. New hex needs the Colorist's sign-off.

### Schedule (IST; T0 = producer spawn ≈ 02:50 IST, Sat 24 Oct)
| IST | Milestone |
|---|---|
| T0 ≈ 02:50 | spawn all 9; Editor starts with R1-R8 + H0 proof; Colorist builds LUTs on library stills; FX kit; MG1-3 build on stills/placeholders; QC builds the animatic; Sound runs checks + master v1 |
| +20 (03:10) | animatic → Director timing pass (10 min); kit v1; LUTs v1; R1-R8 + H0 plates |
| +40 (03:30) | all plates + graded plates; sound master v1; `name_layout.json` |
| +65 (03:55) | MG1/MG2/MG3 540 proxies → **Director review 1** (notes by 04:05) |
| +90 (04:20) | fixes in; comp lead's full 540 master proxy + QC → **Director review 2** (by 04:30) |
| +100 (04:30) | **4K render** (750 f), run as two halves f0-364 / f365-749 in parallel (the only 2 heavy jobs on the box; nothing else heavy runs), est. 35-50 min |
| +150 (05:20) | concat frame-exact, mux master audio, QC on the 4K → **deliver ≈ 05:35 IST** |
**Heavy-job queue:** Editor's minterpolate (R7 is frame-blend, C1, C6, H0, tiles) → MG proxies (one at a time, alternating) → master proxy → 4K halves (alone).

## 11. The Short: thumb-stopping moment
**f365-370**: ink split open by 8 coloured rays, the name forming from 8 coloured copies into white, Balrog's glove landing in the window below. Cover/poster frames: **f374** (name settled, rays still out) and **f749** (the final card). The comp lead exports both as 4K PNGs.

## 12. Risks and fallbacks
- **Name too wide** (Unbounded is wide): scale all 3 lines together to ≤ 1880 px; never squeeze letter widths; if cap drops under 200 px, switch tracking to 0.
- **Duotones look flat on dark plates (R7 Bison, R8 Honda are dark):** Colorist lifts the pre-curve per plate; the fighter must read as a face at phone size (QC checks at 1080x1920).
- **Rainbow cheapness:** if the strike or wall reads "rainbow", drop ray/plume saturation 20% and widen the White Hot core; hues stay but quieter.
- **H0 contact can't be found cleanly:** use F8 (Ken & Ryu back to back, sf120) at 1.0x on f365, no slow-mo.
- **Slow-mo warps** (C1 0.7x, C6 ramp, H0 0.3x): frame-blend instead; H0 may hold a 4-frame freeze on contact.
- **4K render slow:** render halves as one queue; if > 60 min estimated, drop sparks to 120 and plume resolution to 1080 (upscaled bg only, never type).
- **A Whisper re-check on the master finds a new phrase:** Sound escalates; the Director re-cuts S4's in-point inside the chant on a beat (cues regenerate; every downstream frame is cues-driven).
