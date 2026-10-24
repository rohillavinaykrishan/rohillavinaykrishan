# sh010 - VFX Supervisor review - mograph v001 ("PARALLAX")

Reviewed: `shots/sh010/mograph/v001/render/sukanya_mograph_4K.mp4` (2160x3840, 25 fps, 375 fr, 15.00 s) with
`shots/sh010/sound/v001/mix_master.wav`. Review mux: `review/sh010_mograph_v001_review_mux.mp4`.
Method: a frame every 12 (0.48 s), 100% 4K crops at f250/264/271/290/300/340, a phone-scale strip (540x960) of
f0/271/290/374, per-frame audio RMS, and a side-by-side against Vinay v3.

## Verdict: NOTES:

What already works (keep it): the piece is clearly a different film from Vinay's. Fire/gold roll plus colour line-up
against silver B&W, lime, 3D field, Bodoni. No shared template. The snap at f271 is frame-accurate: the audio peak is on
f271 (+7 dB jump) and the plate cut, the zero residuals and `SOLVED · ERR 0.18 px` all land on it. The 4K type is
vector-sharp at 100%. The silver logo reads as chrome. There is no chroma in the plate, so no blue cast. Spelling is
correct everywhere: SUKANYA DILIP DHARIYA / SR. MATCHMOVE ARTIST / STREET FIGHTER · DNEG. The title stinger onset is
13.012 s (f325). The trailer flare pre-build sits on f323-324 and the streak reveal on 325 is in sync.

The problems are all in hierarchy and legibility, and the first one blocks delivery.

### 1. MUST FIX (producer's note): her name is not the hero at the solve. Dept: **mograph**
At f271 every list name is the same Archivo 500, about 37 px, about 85% pearl. Hers differs only by ivory plus a lime
underline. Shown at 540x960 (phone), she is one line in a list of 46 rows. The 1-frame lime glow sits on her "+" marker
and the list centre, not on the name. At f290 the list dims, but her name is still about 37 px list type: about 590 px
wide on a 2160 frame, so roughly 7 px cap height on a phone. Nothing gives her a moment until the Bodoni card fades in
at about f300.

**Design to build (frames are at 25 fps):**
- **f271-275, isolate.** Her row snaps to Ivory `#F4EFE6` at 100%. On the same frame give her name a soft dark halo
  behind it (an ink `#070707` radial at 60%, about 1400x300 px) so it separates from the plate. Over 4 frames all 90
  other names drop to **15% opacity with a 3-4 px blur**. The list must still be there as a texture of the team; it does
  not need to stay readable after the snap. The lime underline still draws in 5 frames. Move the lime glow to her name:
  a 2-frame `rgba(198,255,61,.35)` bloom along the underline, not a blob on the "+".
- **f276-292, lift.** Her name detaches from the plane (z toward the camera, the same system you already have) and
  scales from about 590 px to **about 1800 px wide** (Archivo 125/600 caps, letter-spacing 0.06em). Ease it to
  **frame centre, x 1080 / y 1920**, with an easeOutExpo-style curve so most of the growth happens in the first
  8 frames, on the hit's sustain. As it grows, the list keeps falling back (your dolly back) to about 8% and the plate
  dims to about 0.40 behind it. On about f284, one **lime glint**: a thin, 20-30 px wide diagonal specular sweep across
  the letters at about 40% lime, about 8 frames. It is a solved-track highlight, not a starburst, and it is the only lime
  on screen at that moment.
- **f292-300, hold.** Big, sharp, alone, centred. This is the phone thumb-stop frame.
- **f300-312, focus pull** to the title (your existing rack Archivo → Bodoni), now at matching scale. The Bodoni
  `SUKANYA / DILIP DHARIYA` block should resolve where the big name sits and settle up to its card position. Keep it a
  focus pull, never a morph or a slide.
- Acceptance check: at 540x960 her name at f292 must read from arm's length, and on every frame from 276 to 374 it is
  the largest and brightest element on screen.

### 2. Title card: the Bodoni hairlines vanish at phone size (f300-374). Dept: **mograph**
The font file is the static `BodoniModa-500.woff2`. It is the high-optical-size cut, so the hairlines are about 1-2 px
at 4K. On a phone, `SUKANYA` reads as "SUK\NYA" (the left stroke of each A and the diagonal of the N disappear) and
`DHARIYA` reads as "DH\RIY\" ("DIIARIYA"). See the phone strip, f374. Fixes:
- Use the **variable** Bodoni Moda from Google Fonts (axes opsz 6-96, wght 400-900). Set
  `font-optical-sizing: none; font-variation-settings: "opsz" 14;` (try 11-18) at **wght 600**. The low optical size
  roughly triples the hairline weight and keeps the Didone contrast.
- If the variable font cannot be used, take the 700 static instance and add a 2 px ivory `-webkit-text-stroke`, applied
  only to `#t1, #t2`.
- Re-check the auto-fit afterwards: the heavier cut is a little wider. The widest line must stay ≤ 1760 px, and the
  1800 px lift in note 1 has to land on this width.

### 3. Lime rule strikes through "DILIP DHARIYA" (about f296-304). Dept: **mograph**
At f300 the lime underline, travelling up from the field name, crosses the **baseline of DILIP DHARIYA** from the P of
DILIP to the R of DHARIYA, so it reads as a strike-through. A blurred ghost of the Archivo name also sits between the two
Bodoni lines. Keep the rule hidden (or at opacity 0) until the Bodoni block has settled. Then draw it at its final
y ≈ 2120, centred under DHARIYA with clear space (≥ 60 px below the baseline, as on f340). The Archivo ghost must reach
0 before the Bodoni text is more than 50% opaque.

### 4. Field act reads as clutter, not design (f60-228, worst at f170-228). Dept: **mograph**
Every name's lime residual runs to a solved position in one narrow two-column strip, so they all converge on a vertical
spine. The result is a dense spider-web cone down the middle of frame. The names are mostly 10-20 px smears (unreadable
on a phone), and the long streaked rows at the top (f170-228) look like render artefacts.
- Draw residuals for only about 30 names (the nearest to the camera plus hers). Drop their opacity to about 0.30
  (hers 0.9), and cap the length at about 600 px with a fade toward the solved end, so they read as vectors rather than
  strings.
- Raise the field names' scale floor so the in-focus band is ≥ 48 px cap height at 4K. Let the far ones dissolve into
  fog instead of drawing as 15 px grey dashes.
- Keep 2-3 big foreground names sweeping past the lens (f168-180, "SHAIK RAHEEM / SEKH MASIUR RAHAMAN" works). Those are
  the moments that sell the 3D.

### 5. Pre-solve pile-up and point cloud (f240-268). Dept: **mograph** (+ **roto** for the points)
- At f255-268 the half-collapsed list stacks names on top of each other (f264: hers collides with "SUKHBIR GILL" and
  "SUMIT KUMAR MOHANTY"; there are doubled rows near the top). That looks like a glitch in the last frames before the
  hero. Fix: from about f250, keep her name sharp, ivory and on top (z-index above the field, 100% opacity), and fade
  any name whose screen box overlaps hers to ≤ 20%. Alternatively, shorten the overlap window by changing s(t) to
  easeInOutQuint.
- The point cloud reads as a head in profile at f240-250, but not as a face. Then at 271 it scatters as a dot field
  over the hair and shoulders. Raise the edge share to about 80% (eyes, brows, lips, jaw), use 4 px dots at alpha up to
  1.0, and thin the random fill. Hold the dots for 3 frames after 271 so the registration onto her face is visible
  before they fade.

### 6. Plate too dark at the start (f0-25). Dept: **color** (+ **mograph** for the grid)
f0 has a mean luma of about 8/255. Chun-Li is barely there under the grid, so on a phone the first frame reads as black
with a wireframe. That is a weak thumb-stop.
- Give P1 its own lift in color: about +0.7 stop, keeping the crushed toe. Target a mean luma of about 25-30 at f0,
  with her face and the window shaft clearly readable.
- In mograph, open P1 at opacity 1.0 (not 0.95), and drop the lens grid to about 12% over the centre third of the frame
  (use a radial falloff so the curved edges of the grid stay visible).

### 7. Minor polish (do if cheap)
- **mograph**: the title card's lower half (y 2500-3840) is empty black from f325 to the end. Raise the P9 window and
  silhouette plate to about 0.40 in the lower third, or move the whole card group down about 150 px, so the poster frame
  feels composed rather than top-heavy.
- **mograph**: at f340 the lime "+" left of `SR. MATCHMOVE ARTIST` is at about 50% and reads as dirt. Take it to 100%,
  14 px, or remove it.

## Not requested
No new CG, no Blender, no re-render of the plate beyond the P1 lift. Everything above is HyperFrames/CSS/canvas plus one
colour tweak. The 4K re-render is about 6 minutes.

Priority order: 1, 2, 3 (blocking) → 5, 4 → 6 → 7.

STATUS: notes
OUTPUTS: /home/user/rohillavinaykrishan/projects/sukanya-credit/review/notes_sh010.md,
/home/user/rohillavinaykrishan/projects/sukanya-credit/review/sh010_mograph_v001_review_mux.mp4
