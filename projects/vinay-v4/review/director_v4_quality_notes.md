# Director notes v4: client QUALITY bar (review/client_quality_reference.jpg)
GROUND TRUTH stays as designed: same concept, same cut, same palette families. These notes raise **picture quality, richness and legibility** to the client's reference.

## What the reference is asking for (and what it is not)
I read the reference closely. Its qualities:
1. Everything is **crisp at 100%**.
2. **Rich contrast**: deep blacks, saturated colour, hot rim light and glow on the edges.
3. A **bright, clean, highly legible list**: white caps on near-black, generous pitch, a thin glowing divider.
4. The honoured name **unmistakable**: bold, bigger, on a painted brush-stroke plate with a glow.
5. A premium logo/header with rim glow.

It is **not** a request to change the concept, go red/gold, or turn the piece into a poster.

What I saw in the current build (look_test_v001, lighting proxy check_v1, title p10, mograph snaps r1), measured against that bar:
- **Credits act:** the list is dim grey on near-black. His row barely separates from the others. The text is a 3x upscale of a 720-px video, so it is soft. **Weakest part against the reference.**
- **UI acts (TRACK/SOLVE/FINAL):** 55-60% of the frame is a muddy brown bleed. They read dark and flat on a phone.
- **Plate grade:** correct and clean, but muted: saturation 0.88 and greens at 0.70 look washed next to the reference.
- **Shot monument:** flat cream, little modelling, and small (365-409 px of 1280).
- **Title:** the monument sits in the left half; the sky is a muddy brown; there is no rim and no glow; the type is small. The placeholder is stretched in the mograph snap.

## Department notes

### motion-graphics-artist: CREDITS act (f0-68). Highest priority.
1. **Re-set the list natively.** The roll video stays only as a glow underlay. Build the visible rows as DOM text from `source/credits.txt`, verbatim, with every blank group gap, using the editor's `row_track.json`:
   - left column right-aligned at x = 346·3 = 1038, right column left-aligned at x = 377·3 = 1131
   - row pitch 23·3 = 69 px
   - y follows the measured scroll (827.4 → 486.7 src px over f0-68, ×3)
   - Font: Inter Tight 500, all caps, 40 px, letter-spacing 0.05em, **Bone `#F2EBDF` at 88%** (not grey).
   - Put the graded roll video underneath at 30% with `blur(3px)`. Because the native text lands exactly on the source glyphs, the soft source becomes a free glow under crisp type.
   - Gate: overlay diff at f0 / f38 / f68, ≤ 2 src px of drift on every row.
2. **Header:** re-set "Thanks to our talented teams!" (the source wording, verbatim) in Inter Tight 700, 64 px, letter-spacing 0.12em, Bone. Under it, a 1400x2 px hairline in Marker Pink with a soft glow (`box-shadow 0 0 24px rgba(255,46,136,.6)`); this is our version of the reference's glowing divider. Add a 2 px centre column rule in Bone at 18% between the columns. The bone logo at the top gets a rim glow: a screen-blended copy of `sf_logo_bone.png` blurred 18 px at 30%.
3. **His row: unmistakable**, our version of the reference's gold brush plate. The palette stays pink, not gold.
   - From f0 his row is **Inter Tight 800, 1.22x size (49 px), Bone 100%**.
   - At the lock (f45) a **Marker Pink brush-stroke plate** paints in behind it, left to right, in 6 frames (ease-out).
   - Build the plate as an SVG rect with rough edges: `feTurbulence baseFrequency 0.02/0.35, numOctaves 3` → `feDisplacementMap scale 26`, plus 2-3 dry-brush streaks extending 120 px past each end. Seed fixed, no per-frame noise.
   - Size: about 1.15x the name's width, 84 px tall. Glow: `drop-shadow(0 0 40px rgba(255,46,136,.55))`.
   - On the plate the name turns **Ink `#12100D`** (contrast about 6:1; bone on pink would only be about 2.3:1).
   - The partner name in the same row (VAMSI KRISHNA EADALA) stays at the normal list style.
   - Keep the `TRK 01` bracket, but it now *frames the brush plate*. It flies out to the band corners at f60-68 as planned.
   - Other rows dim to 60% after the lock, not 35%: the list must stay bright and legible.
4. **High-grade characters (authentic to the real roll):** the real crew roll ends in the character line-up, which colour v001 faded to Ink. Use it on purpose instead, in this act only.
   - Asset: `assets_prev/lineup.png` (2880x1760), face-restored (colorist, below), placed **downscaled** to 2160 wide (0.75x, so it is crisper than its source). Crop to the characters, about src rows 560-1760 → 900 px tall, sitting at y 2940-3840.
   - Keep its **native colour and saturation**. That is the richness the reference shows, and character costume colour is designed colour, not a blue cast.
   - Top edge: a gradient to Ink over 300 px, so the red sky never shows.
   - Rim glow: a screen-blended copy blurred 30 px at 25%.
   - It fades out with the roll at f60-68.
   - **Not on the title card**: v3 ended on the line-up, and at title size its blocky bodies would break the ultra-HD promise.
5. Credits background: an Umber `#2A211A` → Ink radial gradient (lighter centre), not flat Ink.

### motion-graphics-artist: UI acts, type and glow (f69-272, title type)
6. **Ambient bleed:** raise it from 22% to 40%, saturate it 1.1, and use `blur(40px)` instead of 60. Add a radial Ink vignette (centre 0%, edges 70%). The phone screen should feel lit by the shot, not muddy.
7. **Band light-spill:** each plate band gets `box-shadow: 0 0 140px rgba(242,235,223,.16)` plus a 2 px Bone edge at 25%. This is the reference's "glow around the art".
8. **Legibility on a phone:**
   - Act labels: 54 → **76 px**, Inter Tight 700, Bone 100%, pink number.
   - HUD: 30 → **36 px**, JetBrains Mono 500, Bone 85%; values in Bone 100%.
   - Breakdown band labels: 28 → 34 px, on a 60% Ink pill.
9. **Graphics glow:**
   - Pink track markers 12 → 16 px, line 3 px, with `drop-shadow(0 0 10px rgba(255,46,136,.7))`.
   - SOLVE point cloud: points 3 → 5 px, drawn with `globalCompositeOperation='lighter'`, plus a second pass at 14 px and 12% alpha for bloom. Point brightness ×1.25.
   - Frustums: 2 → 3 px.
   Still deterministic and drawn from time.
10. **FINAL act: a bigger hero.**
    - Animate the window scale from **×1.30 at f169 to ×1.55 at f220** (easeInOutSine), centred on the monument (`anchor.json` centre x, Gaussian σ 6, clamp so the window stays inside the plate). This takes the monument from about 30% to about 50% of the frame width by the end of the act.
    - The CG stays at its 2808 render; the scale up to 1.19x is absorbed by the plate-match degrade, so there is no extra render cost.
    - Keep the landing jolt at f173.
11. **Title type:**
    - `SR. MATCHMOVE ARTIST`: 96 → **112 px**, Inter Tight 700, Bone 100%, `text-shadow 0 0 28px rgba(242,235,223,.35)`.
    - `STREET FIGHTER · DNEG`: 64 → 72 px, Inter Tight 600, Sand.
    - The pink rule gets the same glow as the header hairline.
    - Logo with rim glow (as in note 2).
    - Fix the placeholder aspect (the title stills are 2160x3840; use `object-fit: cover`, never stretch).
12. Render: HyperFrames at a native 2160x3840 canvas, `deviceScaleFactor 1`. Nothing rasterised small and scaled up: no `will-change` on text, and no CSS `scale()` above 1.0 on any text layer (animate font-size or a 4K canvas instead).

### colorist
13. **Plate grade v002: richer, still sun-bleached, no blue.**
    - Saturation 0.88 → **1.00**.
    - Greens: saturation 0.70 → **0.85**. Keep the sage hue shift at 65% → 50%.
    - Skin and the red suit: saturation 1.08.
    - Contrast: toe pulled down (black point stays Ink `#12100D`, but 10% grey → 7%), mid-slope +8%, keep the creamy tanh shoulder.
    - Target mean Y +3 to +8% vs source; local contrast comes from note 17 (not from the LUT).
    - QC unchanged: B ≤ G ≤ R on the frame and on the sky, VAVG ≥ 128. Deliver `sunbleach_v002.cube` + a before/after sheet.
14. **Credits duotone v002:** the list is re-set natively (note 1), so the roll is only a glow underlay now.
    - Grade it so the text goes to Bone 100% and the background to Umber `#2A211A` (not Ink): `hue=s=0,curves=master='0/0 0.30/0.08 0.55/0.80 1/1'`, then the Ink→Bone duotone map.
    - Measure that text pixels land at Y ≥ 220.
15. **Line-up asset:**
    - Command: `vfx-python tools/vfx/bin/restore.py assets_prev/lineup.png <out>.png --no-upscale --face-strength 0.6`.
    - My test is at `shots/sh010/director/v002/restore_test/ab.png`: 1300x700 crop, 3 faces restored in 85 s. The faces get sharper and natural; the bodies keep their macro-blocking. That is exactly why the art is used downscaled 0.75x, at the bottom, in this act only.
    - Expected time for the full image: about 4-6 min, light/medium CPU. Run it when fewer than 2 heavy jobs are running.
    - Then warm-match it (shadows toward Umber; costumes untouched) and output `lineup_restored_2160.png` (2160 wide, RGBA, top gradient alpha).
    - Compare face-strength 0.6 vs 0 and keep the more natural one.

### lighting-artist
16. **Title (the money frame). Re-light before the final stills.** The 64 spp `title_bg` render running now (started 18:03) is the old design: stop it to free the slot, unless it finishes within minutes and you only reuse its ground. New design:
    - **Framing:** the monument fills **≈ 88% of the width (≈ 1900 px), centred**. The top of VINAY is at y ≈ 900; the plinth base at y ≈ 2350. Camera 0.35 m high, 32 mm-equivalent, a slight upward look so the letters tower against the sky.
    - **Light** (the reference's rim + glow, in our palette):
      - **Key = low sun behind the monument**, elevation ≈ 12 degrees, 15 degrees right of centre: a hot rim on every top/right edge, long shadows running toward the camera. The darker foreground makes the type below read.
      - **Front fill:** a large warm area light (`#F2EBDF`) front-left at ≈ 30% of the key, so the front faces read Bone at ≈ 65-75% luminance. Legibility first.
      - **Marker Pink kicker:** a small area light right-rear at low energy: a thin pink edge on the left sides of the letters. Keep it ≤ 3% of pixels.
    - **Sky:** Ink (top) → Umber → a hot Sand/Bone horizon glow, with the sun disc low behind KRISHAN/ROHILLA (it will bloom through the gaps between letters).
    - **Material:** bone plaster, roughness 0.55 → 0.42, coat 0.1, bevel 0.02 → **0.035** (the bevels catch the rim); dust gradient on the bottom 15 cm.
    - **Comp in Blender:** Glare node (Fog Glow, threshold 0.9, size 8), plus a Streaks glare at 4% for the sun; mist pass for haze; no denoiser artefacts on the rim (OIDN with albedo + normal passes).
    - **Output** as planned: `title_fg` (RGBA) + `title_bg` at 2160x3840, 64 spp. Show a 540x960 proxy to the director first (≈ 15 s).
17. **Shot monument (in the plate): modelling, not flatness.**
    - Lower the world fill 0.5 → 0.3 so the backlit front faces sit at 55-65% of the sunlit sand.
    - Bevel 0.035 so the rims read.
    - Sun azimuth locked to the real shadows on s25.
    - Contact shadow under the plinth must reach Umber density about 0.75.
    - Keep the 2808 final width (no cost increase).
    - Show the director s0/s25/s51 at proxy again before the 52-frame run.

### compositor
18. **Sharpness and integration:**
    - Plate: lanczos up, then **`cas=0.55`** (contrast-adaptive sharpen) at band res; no `unsharp` haloes on the sky edge.
    - CG: match the plate's softness only as far as needed (σ ≈ 0.7, not 1.0), so the monument is the crispest thing in the frame without looking pasted.
    - Light wrap 4% from the sky.
    - **Rim bloom:** threshold the CG's top 8% luminance, blur 12 px, screen 35%.
    - Luma-only grain matched to the colorist's (no chroma grain).
19. **Encode:**
    - 4K master: libx264 `-preset slow -tune film -crf 12 -pix_fmt yuv420p -profile:v high`.
    - Share copy < 16 MB: 2-pass at about 8.2 Mbps video + 128 kbps AAC, `-tune film`.
    - Check a 100% crop of the list text, the brush plate edge, the monument rims and the logo on both files.

### roto
20. With the FINAL window growing to ×1.55, **the holdout edges get 2.7x larger than the plate**.
    - Build the matte at 2x (2560x1072): rembg matte upscaled, then an edge refine guided by the plate (`cv2.ximgproc.guidedFilter` if available; otherwise a joint-bilateral approximation with radius 4).
    - Temporal median over 3 frames, erode 1 px at 2x, feather 2 px.
    - Check over black and white at 100% on s4 (the landing), s25 and s48.
    - Blade/helicopter: SAM 2 only if `review/monument_bbox_vs_blade_heli.png` shows an overlap with the final (×1.55) window.

## Director decision: sound blocker (from sound v001)
Sound is right and I missed it: my clip pass did not hear **"You lose"** (117.37-118.46) or **"I'm a street fighter"** (from 126.16). Decision, with no window change and no picture recut:
- **"You lose":** remove it by **extending the trailer's own silence**. The bed fades to silence 117.30 → 117.38 (80 ms, after the tail of the f121 hit) and stays silent until the existing near-silence ends at 118.70. 118.70 onward is untouched, so the f173 re-entry is intact. This is a removal edit of the real music: nothing is added and nothing is synthetic. The REGISTRATION beat becomes a 1.4 s held breath (f130-167), which suits the solve even better.
  - Gate: Whisper small + medium on the new bed hear no words in 116-119.
  - Mograph: nothing changes.
- **"I'm a street fighter":** use sound's `mix_master_altfade_13.40-14.00.wav` fade. The last second of the title holds over the bed's decay to silence (a clean poster hold for a Reels loop).
- Re-master to -14 LUFS / ≤ -1 dBTP; onset QC f173 / f275 ±1.

## Cost (4 cores, heavy ≤ 2)
| Item | Who | Extra time |
|---|---|---|
| line-up face restore | colorist | ~5 min (medium CPU) |
| title re-light proxy + 2 stills at 64 spp | lighting | ~15-18 min in one heavy slot (replaces the current title run) |
| shot monument tweak (proxy) | lighting | ~3 min; the 52-frame run cost is unchanged |
| grade v002 + duotone v002 | colorist | ~15 min |
| native credits list, brush plate, glows, scale ramp | mograph | ~40 min build; the 4K render grows ~10% (glow filters) |
| 2x matte refine | roto | ~5 min |
| bed silence edit + re-master | sound | ~10 min |

Net: about **+30-40 min wall clock**, which fits the budget. Approval gates (director): (1) colorist v002 sheet, (2) title proxy 540x960, (3) mograph snaps at 0.3 / 1.9 (brush plate) / 2.6 / 6.92 / 8.6 / 9.4 / 11.0 / 14.4 s.
