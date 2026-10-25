# Treatment - "The Beekeeper 2" trailer re-cut ("The Hive Turns")

Director, v001. Inputs: `shots/audio/audio/v001/` (notes, analysis.json, dialogue.json),
`shots/edit/log/v001/` (footage_log.json, notes.md), `review/footage_contact_sheet.jpg`.
I looked at every shot on the contact sheet, all of s002 sampled every 2 s, and s041 frame by frame.

## 1. Logline and concept

**Logline:** They built the most dangerous operative alive. Now the hive has gone rogue, and the
man who keeps the bees is the only sting left.

**Concept for the cut:** *gold is the hive, teal is the world it has poisoned.* The trailer opens on a
single bee walking across Clay's hand at dusk (s002, the best image in the footage). The source
cut wastes it on a slow 16 s tilt with nothing linking it to what follows. This cut makes the bee the
spine of the picture. It is the first image and the last, a honey-gold emblem marks the enemy, and
the grade moves from cold steel-teal order (the government, the park, the tarmac) to burning amber
as Clay brings the fight to them. Fire, the Super Bee badge and the title are the only places
where the gold runs at full strength.

What changes from the source cut:
- **Soundtrack untouched and in order** (it is the spine). Only the 0.5 s silent head and the 12 s
  silent tail and red bumper (s061) are removed. All lines stay whole.
- **Picture re-timed to the hits.** Every big hit (19.53, 30.19, 37.43, 40.77, 47.67, 54.89, 60.74,
  71.82, 74.77) gets a cut or an event. Several source cuts fall 0.1-0.3 s off the music. For
  example, the logos land at 19.85 but the boom is at 19.53.
- **The mid-trailer title (s042, 55.26-59.10) is removed.** The title moves to the 71.82 slam, the
  biggest late hit, where it belongs. The freed 3.8 s becomes the tunnel set-piece breaking in
  early, so the action rises without a pause instead of stopping for a card.
- **Proper end:** pre-title line, then TITLE, then RELEASE CARD, then a bee button on the final hit,
  then black. Ends at 76.1 s.
- All burned text cards (s017, s018, s042, s060) are rebuilt clean in one title style.

## 2. Timing convention

All times below are **A-time = source audio time** (`source/trailer_audio.wav` = picture time of
`trailer_original.mp4`). The cut starts at A 0.50, so **output time = A - 0.50**. The cut ends
at A 76.60, which is **76.10 s output = 1826 frames @ 24 fps**.
Beat grid: ~0.49 s (analysis.json `beats_s`). Snap every cut to a listed beat or hit, or to its
8th-note subdivision (0.245 s = 6 frames).
Fps: spec is 24, source is 23.976. Conform picture and audio together by 1001/1000 (picture
frame-for-frame, audio `atempo=1.001`). This adds no dup frames and shifts the timeline by
0.075 s over 75 s, which is negligible. Or keep 23.976 timing and let the conform happen once in
delivery. **Editor decides once and notes it.** Never mix the two.

## 3. Emotional arc

| Act | A-time | Feeling | Energy |
|---|---|---|---|
| Cold open | 0.50-19.53 | stillness, menace in calm, "a legend at rest" | 0.4 to 0.6 |
| Logos | 19.53-21.50 | first blow | spike |
| Setup | 21.50-30.19 | threat: the hive has gone rogue, the state is the target | 0.8, booms every ~1 s |
| Recruitment | 30.19-37.43 | dry wit, pride: "my way" / "nothing less" | 0.4, breath |
| Gear-up | 37.43-47.67 | swagger, the toy reveal (Super Bee) | 0.85 |
| Action peak | 47.67-58.90 | release, catharsis, carnage on the tarmac, then into the tunnel | 0.92 |
| Breath | 58.90-61.25 | "Welcome back, Clay.", the legend returns | 0.78 |
| Climax | 61.25-69.50 | fury, the hive's sting at full speed | 0.9 to max |
| Pre-title | 69.50-71.82 | the smirk: "Next time, don't be so hard-headed." | 0.7 |
| Title / card / button | 71.82-76.60 | brand slam, date, last sting, black | hit, hit, hit, out |

## 4. Act structure and shot plan

Burned text and logos are allowed only in the logo beat. Shots marked **SYNC** have on-screen
dialogue. Keep them at their source position (no slip). Speed ramps use
`grade.sh slowmo` / minterpolate. Use 0.5x minimum, and only on shots with little fast motion.

### COLD OPEN, A 0.50-19.53 (hook: the bee on the killer's hand)
| A-time | Shot | Notes |
|---|---|---|
| 0.50-0.70 | black | Silent head, trimmed to 0.2 s. |
| 0.70-3.59 | s001 | Silhouette, muscle car, smoke plume. The baked fade-up finishes by ~0.6. Hold. Slow digital push 100 to 104 %. |
| 3.59-19.53 | s002 | Keep the continuous tilt, untouched in time. The hand on the hood with the bee (3.6-9 s) is the hook. The bee lifts off as the VO says "most dangerous operative" and hovers by his face through "gone rogue". He lifts his eyes on "you're the only one who can stop them". Add a slow 100 to 108 % push across 14.5-19.5 (riser). |
| 12.05 and 13.27 | flash-forward | Two **3-frame** flash-forwards at the 12.05 boom ("now") and on "rogue" 13.71: s006 villain hall, then s047 fire jet. Use amber, never white. They are subliminal and give a taste of the hive and the fire before the logos. That is the teaser hook. |

### LOGOS, A 19.53-21.50
| 19.53-20.50 | s003 MGM | Cut ON the 19.53 boom (source is late by 0.32 s). |
| 20.50-21.50 | s004 Miramax | Out before the VO starts at 21.65. |

### SETUP, A 21.50-30.19 ("The beekeepers want complete control...")
| A-time | Shot | Notes |
|---|---|---|
| 21.50-22.50 | s005 | Gold honeycomb emblem on "The beekeepers". The hive is gold. |
| 22.50-23.48 | s006 | Platinum-haired leader in the torch-lit hall. Out on boom 23.48. |
| 23.48-24.94 | s007 | DC night aerial at 0.66x on "complete control of the government". Lift the exposure (see section 6). |
| 24.94-25.94 | s008 | SYNC-safe: keep source position. |
| 25.94-26.98 | s009 | Irons OTS. Keep source position in case of lip sync on "they're prepared to kill". |
| 26.98-27.52 | s010 | Agent touches earpiece and raises her hand. Trim to the hand raise. Out on boom 27.52. |
| 27.52-29.30 | s011 | Corridor fight, head of the shot (no blur). |
| 29.30-29.55 | s011 tail | The motion-blur tail used as a whip into the suck-out. |
| 29.55-30.19 | black | Suck-out = black. |
| 30.19 | flash frame | 2-frame amber flash (#F2B544 at 70 %) on the BOOM, then black. |

### RECRUITMENT, A 30.19-37.43 (SYNC, source-locked)
s012 black and s013 baked fade-in (31.11), s014, s015, s016 stay exactly at source position: "If we're
gonna go up against the beekeepers, we're gonna do it my way." / "I would hope for nothing less."
Cut s016 at **37.43** (the slam, 0.23 s earlier than the source). Nothing else moves. The near-silence
is the point.

### GEAR-UP, A 37.43-47.67 ("I got you a car")
| A-time | Shot | Notes |
|---|---|---|
| 37.43-38.27 | NAME CARD | Rebuilt "JASON STATHAM" on one card in the title style, replacing s017/s018. On the slam. |
| 38.27-38.78 | s021 | Irons' knowing smile, setting up the line. |
| 38.78-39.26 | s019 | Clay in the car, glancing back. |
| 39.26-40.77 | s020 | Car wide down the tree-lined road at ~0.55x. The whole line "I got you a car" plays on the reveal and the riser. |
| 40.77-41.82 | s024 | IMPACT: the grille guard rolls at the lens. |
| 41.82-42.33 | s022 | Hidden lever (dark, lift). |
| 42.33-42.82 | s023 | Boot on pedal (very dark, lift; drop it if the lift is noisy and extend s022/s024). |
| 42.82-43.33 | s026 | Car on the apron, team approaching. |
| 43.33-44.84 | s025 | **Super Bee badge** rack focus at 0.75x on "Dodge Super Bee" (43.74). This is the first full-gold accent in the cut. |
| 44.84-45.79 | s027 | Impact 44.84: over-the-shoulder, the car surrounded. |
| 45.79-47.67 | s028 | Clay grim behind the wheel: "Fully loaded with Stinger." Hold to the riser. |

### ACTION PEAK, A 47.67-58.90 (music only, no title card here any more)
| A-time | Shot | Notes |
|---|---|---|
| 47.67-48.05 | s029 | BIG IMPACT: hand hits the weapon panel. |
| 48.05-48.67 | s030 | Scarred car profile. |
| 48.67-49.57 | s031 | Clay pulls up the mounted gun (0.8x). |
| 49.57-49.95 | s032 | Hit 49.57: muzzle bloom (accept the clip; halation). |
| 49.95-50.60 | s033 | Money shot: silhouettes and explosions. |
| 50.60-51.08 | s034 | Through the cracked windscreen. |
| 51.08-51.55 | s036 | Hidden barrel fires. |
| 51.55-52.52 | s035 | Top-down drone, car spinning (0.73x). This is the one wide breath. |
| 52.52-52.99 | s037 | Soldiers foreground, burning car behind. |
| 52.99-53.48 | s038 | Soldier aiming, tracers. |
| 53.48-53.94 | s039 | Embankment explosion. |
| 53.94-54.89 | s041 TAMED | Only the dark frames (Clay firing, sparks), max 2 bright frames, see section 5. |
| 54.89-55.87 | s040 | IMPACT 54.89: the **car bursts through the fireball**. Speed ramp 100 %, then 35 %, then 100 %. This is the most thumb-stopping image in the trailer. |
| 55.87-56.35 | s044 | Into the tunnel: masked soldier. Hard cut, steel to amber. |
| 56.35-57.31 | s045 | Flamethrower nozzle sweeps. |
| 57.31-58.26 | s047 | Hit 57.28: the flame jet fills the corridor. |
| 58.26-58.90 | s048 | Hit 58.31: full-frame fireball at camera (0.78x). 4-frame dip to black at 58.90 as the music dips. |

### BREATH, A 58.90-61.25 ("Welcome back, Clay.")
| 58.90-60.74 | s043 | Clay alone in the tunnel, looking up. 0.7x with a slow push. The line is off-screen. |
| 60.74-61.25 | s046 | Impact 60.74: he turns (motion blur) into the climax. |

### CLIMAX, A 61.25-69.50 (tunnel, accelerate)
Shot length falls from ~1 beat (0.49 s) to half-beats (0.245 s) by 66 s.
| A-time | Shot | Notes |
|---|---|---|
| 61.25-62.21 | s049 | Grapple, low angle (lift). |
| 62.21-62.69 | s050 | Soldier shouting and falling. |
| 62.69-63.20 | s051 | Silhouettes (lift; if it is still mud, cut it and extend s049). |
| 63.20-63.69 | s052 | Wide tunnel brawl, fires on the ground. |
| 63.69-64.64 | s053 | Clay swings under the fluorescents. |
| 64.64-65.11 | s054 | Reverse angle. |
| 65.11-65.57 | s055 | Sparks burst. |
| 65.57-66.06 | s056 | Clay firing, orange glow (first half). |
| 66.06-68.50 | **HIVE MONTAGE** | 10 cuts x 6 frames on the 8th notes, using *unused frames* of used shots, alternating the two set-pieces: s040, s053, s036, s049, s033, s047, s034, s056 tail, s032, s045. No white frames; every cut is a different image. |
| 68.50-68.99 | s041 dark frame / s054 | One last look at Clay. Editor's pick, 0.49 s. |
| 68.99-69.50 | s057 | Final burst (0.73x), then black. |

The material is tight here (the old title took 3.8 s). Ramps and the half-beat montage cover
it. Reuse is allowed only as different frames, never the same frames twice.

### PRE-TITLE, A 69.50-71.82
| 69.50-69.90 | black | (s058) |
| 69.90-71.33 | s059 | SYNC/source-locked, baked fade-in: "Next time, don't be so hard-headed." |
| 71.33-71.82 | black | The gap. |

### TITLE, RELEASE CARD, BUTTON, A 71.82-76.60
| A-time | Picture | Notes |
|---|---|---|
| 71.82-73.26 | **THE BEEKEEPER 2** | Rebuilt clean. Gold distressed type (#F5C04A, edge #B8741A) on near-black #07090A with a faint honeycomb texture at 6 %. 2-frame amber flash on the slam, then halation that decays over 12 frames. Inside the 2.39 frame. |
| 73.26-74.77 | RELEASE CARD | Hit 73.26: "ONLY IN THEATERS JANUARY 15" / "IN PREMIUM FORMATS", same type, smaller, white-gold #F3E3C0. No social or billing clutter. Hold 1.5 s for legibility. |
| 74.77-75.38 | **BUTTON** | Final hit: a callback to the bee in flight beside Clay's face (s002, frames from ~11-13.5 s source, punched in to ~115 %). The cut starts and ends on the same bee. |
| 75.38-76.60 | black | Audio hard-cuts at 75.38. Audio dept may add a <=0.8 s natural decay of the 74.77 hit. Then silence. **End.** |

## 5. Cutting style

- **Beat-cut rules:** cuts on beats or hits from `beats_s`, ±1 frame. Fast sections use whole beats
  (0.49 s) or half beats (0.245 s). Never shorter than 6 frames except flash frames. Big hits
  always get a cut, a flash frame or a visible event (explosion, muzzle, impact) *on* the frame.
- **Dialogue:** never cut inside a line's word span. SYNC shots (s013-s016, s059, and s009 to be
  safe) never slip. Off-screen VO can play over any picture.
- **Speed ramps** (ffmpeg minterpolate / `grade.sh slowmo`): s007, s020, s025, s031, s035, s040
  (hero ramp), s043, s048, s057. Use 0.35x minimum only on s040 and 0.5x minimum elsewhere.
  Check for interpolation warping on edges, and fall back to frame-blend if it tears.
- **Freeze frames:** none in the body. Optionally a 2-frame hold at the peak of the s040 ramp.
- **Flash frames:** amber #F2B544 at <=70 % luma, 2 frames, never pure white. Only at 30.19, the
  71.82 title, and inside s041. **Photosensitivity (Harding/Ofcom):** never more than 3 flashes
  in any 1 s window. s041 alternates near-white and dark every frame (about 12 flashes in 0.96 s),
  so it must be rebuilt: use the dark frames, keep at most 2 bright frames >=0.35 s apart, and
  dim them to <=60 % luma. The editor runs the YAVG check on the final cut: no frame-to-frame jump
  over 20 % of luma more than 3 times per second.
- **Dip to black:** 29.55-30.19 (suck-out), 58.90 (4 frames into "Welcome back"), 69.50, 71.33,
  and the end. Baked fades in s013 and s059 are used only in their source-locked spots. Never
  hard-cut into fade frames anywhere else (and not into s001 before 0.6 s).
- **Framing:** crop `1280:536:0:92` and scale to 1920x804 (exact 1.5x), centred in 1920x1080
  with 138 px bars. At 4K that is 3840x1608 with 276 px bars. Don't stack new bars on the old ones.
  Titles stay inside the active picture.
- **Drop:** s061 bumper, s042 and s060 (text rebuilt), s017/s018 (rebuilt as one card), and
  the s011 blur except the 0.25 s whip.

## 6. Colour direction

### 6a. Correction (shot by shot, before the look)
Goal: every shot reads as the same film before any style is added. Work on the cropped
active picture. The numbers are from `footage_log.json` stats (8-bit luma; R/G/B means).

**Neutral balance:** bring greys and whites to neutral first.
- Blue/cyan cast, tarmac and car (B is 6-30 above R): s019, s024, s026, s027, **s028 (B-R +30, Clay's
  skin goes cyan: fix it)**, s029-s031, s035-s038. Warm them toward neutral. The look adds
  the teal back in shadows only.
- Green/yellow cast (G≈R, low B): s010, s011, and tunnel s043 (G-R +14, green fluorescent),
  s046. Pull green out of the mids (toward neutral-teal, never olive).
- Strong orange/olive: s056 (R-B +64), s059 (olive, R-B +38), s006/s005 (deep amber). Keep
  them warm but take the olive out of the s059 skin. s005/s006 keep their gold. That is the hive.
- Dusk s001/s002: magenta-pink sky. Rotate pink toward peach-amber, keep skin natural.

**Exposure match** (target mean luma of the active area):
- Day exteriors (park, road, tarmac): 80-95. s026 (122, flat bright sky) comes down to ~100 with a
  highlight roll-off. s013/s014 skies near clip (p95 219-223) need a soft knee to save the clouds.
- Night/interiors: 45-60. Tunnel s044-s057 sit in 43-79. Even them out to ~50-60 so the fire is
  the brightest thing.
- **Dark shots, lift without noise:** s007 (19 to ~32), s022 (20 to ~35), s023 (22 to ~35),
  s049 (30 to ~42), s051 (21 to ~34), s006 (34 to ~40, keep it moody). Order: **denoise first** (light
  temporal + spatial on these shots only, e.g. `hqdn3d=3:2:5:4` or `nlmeans=s=2.5:p=5:r=9`),
  then lift the **lower mids** with a curve or gamma (0.80-0.85). **Do not raise the black point.**
  Then let the grain pass (6c) cover what is left. Target crush (pixels < Y 8) <=15 % on these
  shots, from 28-52 %. If s023 or s051 still band or crawl at 1080p, cut them (alternatives in section 4).
- Clipping: s032, s047, s048, s041 and fire highlights stay clipped. Hide the hard edge with
  halation (6c) instead of pulling it down to grey.

### 6b. Hero grade ("Honey & Teal")
| Element | Target |
|---|---|
| Highlights | Honey/amber: lift warmth above ~70 % luma, toward #F2B544 / #E8A33D. Specular fire to #FF8A1E. |
| Midtones | Close to neutral, slightly warm. Skin sits on the orange/skin line around #C98E6E. |
| Shadows | Teal #0F3B45 into #082A33 below ~25 % luma. Split-tone, not a global tint. |
| Blacks | Deep but not crushed. Black floor ~ Y 4-6 (8-bit full range) with a hint of teal. No more than 15 % of the frame below Y 8 except on title cards and intentional black. |
| Contrast | Gentle S-curve. Toe stays soft so detail survives in the jackets and tunnel walls. |
| Saturation | Overall 85-90 %. Greens (park grass, trees) pulled toward teal-olive and desaturated 25 %. Reds (Clay's track jacket s008-s016) kept, at -10 %. |
| **Skin protection** | Hue-key skin (about 15-40° hue) and exclude it from the teal split. Clay must never go grey-green or cyan (watch s028, s043, s059). |
| Halation/bloom | Threshold ~85 % luma. Blur ~0.5 % of frame width. Tint red-orange #FF5A1F, screen at 15-25 %. Strongest on fire and muzzle: s032, s033, s036, s040, s047, s048, s055, s057, the title. Barely on skies. |
| Grain | Fine 35 mm, luma only, ~ `noise=alls=5:allf=t` at 1080p (scale with the output). Same strength on every shot, and slightly heavier (alls=7) on the lifted dark shots so they match. Add it after denoise and before the 4K upscale, or re-add a finer pass after the upscale. Don't upscale coarse grain. |
| Vignette | Slight, ~-0.25 stop at the corners (`vignette=PI/5` blended back to ~50 %), inside the 2.39 area only. |

**Palette:** honey #E8A33D | amber highlight #F2B544 | deep honey #B8741A | fire #FF8A1E |
halation #FF5A1F | skin #C98E6E | teal shadow #0F3B45 | deep teal #082A33 | black #07090A |
title gold #F5C04A | card white-gold #F3E3C0.

### 6c. Per-act variations (one look, turned up or down)
| Act | Shots | Variation |
|---|---|---|
| Cold open | s001, s002 | **Golden dusk.** Warmest of the "calm" scenes. Sky peach-amber rather than pink, teal only in the hill shadows. The bee catches a highlight. This is the honey promise. |
| Logos | s003, s004 | Leave them alone (brand assets). Grain and vignette only. |
| Setup | s005-s011 | **The hive is gold, the world is cold.** s005/s006 rich honey-gold with deep blacks. s007 DC night, steel-teal, city lights warm. s008-s011 cooler and desaturated (sat ~75 %), teal shadows. s010/s011 corridor green goes to teal. |
| Recruitment | s013-s016 | Overcast, cool-neutral, sat ~80 %. Protect skin and Clay's red jacket. Highlights roll off. The calmest, coolest scene in the cut. |
| Gear-up | s019-s028 | Steel-teal rain world (fix the blue cast first, then put teal back in the shadows). **s025 Super Bee badge: isolate the yellow and push it to full honey.** It is the first amber accent and the line points at it. |
| Action peak | s029-s041 | **Hotter.** Contrast +10 %, teal shadows deeper, fire highlights fully amber with the strongest halation. Warm/cool separation at its maximum (s033, s040). |
| Tunnel climax | s043-s057 | **Amber takes over.** Tunnel lights become honey, fluorescent green becomes teal, blacks the deepest in the cut (still with detail). s043 ("Welcome back") is the one cool-teal frame with warm skin. Clay surrounded by the hive's colour. |
| Pre-title | s059 | Amber-low key, olive removed from the skin, small vignette increase. |
| Title / card | rebuilt | **Pure gold** #F5C04A on #07090A, honeycomb texture, halation on the slam. The button (s002 bee) is graded as in the cold open, so the cut closes in the golden dusk where it began. |

### 6d. Tools / order of operations
Per shot: crop, then denoise (dark shots only), then balance and exposure (curves/colorbalance/eq),
then the hero look (a shared `.cube` built once, applied with `grade.sh lut`, and per-act trims
after the LUT), then skin protect, then halation, then vignette, then grain. After that comes the
letterbox pad and `grade.sh deliver ... uhd`. `grade.sh look teal-orange` / `blockbuster` is a starting
reference only. The final look must hit the palette above. The colorist delivers a before/after
strip of one frame per act for my review.

## 7. The Short (most thumb-stopping moment)
**s040, car bursting through the fireball (A 54.89 ramp)**, preceded by s047's flame jet.
For a vertical cut-down: s002 bee on hand (1 s hook), then s040 ramp, then s047/s048, then the title.
That is not in this delivery, but it is the moment to use if one is asked for.

## 8. Doable on 4 cores
Everything is ffmpeg: crops, ramps on ~10 short shots, curves/LUT, a blur-screen halation pass and
noise. Rebuilt cards are text over black (ffmpeg drawtext, or `html2png.sh` for the distressed
type). The only heavy step is the Real-ESRGAN 4K upscale of ~76 s. Run it as one background job
under the 2-heavy-jobs rule, or use `grade.sh deliver uhd` (lanczos) if the budget says no.
