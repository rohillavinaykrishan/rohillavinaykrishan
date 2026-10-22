# VFX Supervisor review: sh010 v4 "GROUND TRUTH" (deliver/..._v4_4K.mp4)

Reviewed: the 4K master, 2160x3840, 25 fps, 375 frames, 15.00 s, with mix_master muxed in. I pulled frames every 12 (0.48 s) at phone scale (540 px), every frame for f158-181 and f266-295, and 100% crops of f60, f173, f200, f284, f285 and f340. Audio was measured at 40 ms and 10 ms RMS. For comparison I pulled PARALLAX at 1 fps and also looked at both previous sheets and the client reference.

## Verdict: NOTES (close; 3 must-fix notes, 3 should-fix notes)

What already beats PARALLAX and meets the reference:
- **Credits act (f0-68): the best part, and on par with the reference.** The list is natively set and crisp at 100%. The header and the pink glowing hairline match the reference grammar. The brush plate paints in at f45 and reads instantly on a phone: ink on Marker Pink, with good dry-brush streaks and glow. The line-up art gives the colour richness the reference has. PARALLAX never isolates her name this clearly.
- **SOLVE (f137-168)**: a full-frame point cloud with frustums registering and true numbers. It is richer than PARALLAX's dot cloud, and the registration into the plate at f163-168 is a real "aha".
- **BREAKDOWN (f221-272)**: the 4 stacked bands fill the phone and are genuine VFX-reel language, the strongest proof of craft in any of the three pieces. The fold at f273-274 is clean.
- **Title (f275-374)**: native-4K Cycles monument. The rims, bevels and pink kicker are crisp at 100%, and the type hierarchy is clean. This is clearly more premium than PARALLAX's flat Bodoni card. It loops well on the poster hold.
- **Sync**: the re-entry swell peaks at f172-174 (the landing is at f173), the title cut f275 is on a +5 dB hit, and SR. MATCHMOVE ARTIST lands on f291 (+5.9 dB). Good.

Where PARALLAX still wins: **immersion during TRACK and FINAL (f69-220, about 6 s, 40% of the piece).** PARALLAX is full-frame the whole time. Ours is a 904 px band (23.5% of the height) floating in 76% blurred plate bleed. On a phone that reads as the "blurred-bars repost" look, which is cheap. This is the main reason it is not yet *clearly* better. Notes 1-2 fix it within budget.

## Notes (priority order)

### MUST FIX
1. **mograph: turn the empty bleed into matchmove overscan (f69-136 and f169-220).** Do not clip the solved ground grid and the track "+" to the band. The cameras are solved, so project the 1 m Sage grid (and, in TRACK, the 3D points as faint dots) through each frame's real camera *beyond* the plate edges, out into the area above and below the band. The ground plane continues under the band and the point cloud continues around it, the way an overscan view does in 3DE/SynthEyes.
   - Drop the bleed back to about 20% with an Ink vignette at 80% at the frame edges, so the drawn grid reads as the content and the blur is only atmosphere.
   - Grid at 18-25% Bone/Sage, 2 px. Fade it out toward the top and bottom 300 px.
   - It is still drawn from time and uses the same `cams.json`/`points.json` already in the SOLVE act, so it needs no new solve and no render.
   - Result: the full 9:16 frame is purposeful, it ties TRACK to SOLVE visually, and only someone who has done the job would make it.
   - Check: phone-scale snaps at f84, f113, f190 and f215.
2. **mograph/comp: make the name READ in the hero landing (f169-176).**
   - At f169-172 the falling monument is semi-transparent (ghosted; the dunes show through the letters). Make it solid; use motion blur only.
   - From f173 it is mostly behind the man in black, and it sits about 120 px wide on the phone. Keep the occlusion: it is the proof of integration, and it is honest. To make the moment land:
     a) Move the pink `+ LOCKED` tag from f208 to **f173**, pinned to the plinth (it already follows the 3D anchor), with the 1-frame pink halo. The eye goes to the name on the hit.
     b) Start the window scale ramp a little earlier and harder: ×1.30 at f169 → ×1.45 by f185 → ×1.55 at f220, centred on the anchor.
   - Check: frames f171, f173, f176, f185 at 540 px. The full "VINAY KRISHAN ROHILLA" must be readable on at least f170-172 (the fall) and again by about f185.
3. **mograph: the logo reveal f283-286 is a hard vertical clip.** At 100% (f284, f285) the logo is cut by a perfectly straight vertical edge with no feather. It looks like a mask error.
   - Replace it with a wipe slanted along the logo's own italic angle (about 20 degrees), with a 160-200 px soft edge, over 8 frames as planned (f283-291), not 3.
   - Or simply an 8-frame opacity rise with a 12 px rise in y.

### SHOULD FIX (cheap, visible)
4. **comp: plate macroblocking at the FINAL scale.** At ×1.45-1.55 the trailer's 720p H.264 blocks are visible: f200 on the red suit and the legs, f173 on the man's arm and the dunes. The fighter's knee shows blocks even at phone scale (f192).
   - Before the lanczos upscale, at source res: `deblock=filter=strong:block=8` (or `pp=ha|a/va|a/dr`), then `hqdn3d=1.5:1:3:3`, then the planned `cas`.
   - Apply the same chain in TRACK and BREAKDOWN for consistency.
   - Check: a 100% crop of f200.
5. **mograph/colorist: line-up top edge (f0-68).** The orange-red sky band (y about 2900-3150) is fully visible, against the director's note ("the red sky never shows"). It also edges back toward v3's red/gold.
   - Push the top Ink gradient down about 250 px so the art starts at the characters' heads.
   - Fade the last 2 faded list rows (VIKAS/VIKASH KUMAR...) before they overlap the art.
6. **sound (optional, director's call): f132-163 is digital zero (-inf dB) for 1.3 s.** On a phone, true digital silence in the middle of a piece reads as a dropout, and the `02 SOLVE` act opens on dead air.
   - Fill it with the bed's *own* tail: a reverb/decay of the f121 hit, or the existing 117.30 tail stretched, sitting at -40 to -45 dB and swelling into the f164 re-entry. That is processing of the real music, not a synthetic sound.
   - Re-run the Whisper gate. If the director prefers the hard breath, leave it.

Not requested (keep as is): the title composition, the 2-frame flash at f275, the breakdown, the SOLVE act, the credits type, and the end hold with the audio decay.

After notes 1-3 (about 40-60 min of mograph and comp, no new Cycles renders), I expect to approve. With them it is clearly better than PARALLAX in every act.
