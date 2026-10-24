# sh010 mograph v002 - VFX sup notes (review/notes_sh010_v4.md) 1, 2, 3, 5 + team-lead QC credits blocker
Base: v001 (kept). Inputs: comp v002 PNG sequences (deblocked), colour v002, layout v001, lighting v002, restore r470. 0 placeholders (render/manifest_final.json).
1 Overscan f69-136 / f169-220: the 1 m grid (Bone/Sage, 2 px, 24%) and, in TRACK, the 3D points (faint, 5 px) are projected through each frame's real camera
  outside the band. The lens model is continued past r = 0.9 along its tangent (C1, monotonic) so the ground runs past the plate edge without folding
  (inside the plate, r <= 0.69, it is the exact SIMPLE_RADIAL). Fades out at the top/bottom 300 px. Bleed 20%, Ink vignette 80% at the edges.
  TILT f121-128 blends the band grid and the overscan grid into the viewport grid. Above the band is sky in the solve: atmosphere only, nothing invented.
2 Landing: "+ LOCKED" + halo snap in on f173 at the anchor's front-left plinth corner (target "+" f169-172). Window x1.30 (f169) -> x1.45 (f185) -> x1.55 (f220).
  The fall ghosting was baked in comp v001; comp v002 shapes alpha on s1-s4 (~95% solid). Fighters stay in front (comp holdout).
3 Logo f283-291: clean 8-frame fade + 12 px rise, rim glow follows 2 frames later (no mask edge).
5 Line-up: scripts/sky_key.py pulls the saturated orange-red/yellow sky (top 560 px) to Ink, faces and costumes untouched; Ink gradient only over the top edge.
QC: #credUnder now sits in #credUnderClip with a screen-space bottom fade equal to the native rows' (2480-2660 vs rows 2500-2690); underlay blur sigma 10 (no
  legible ghost letters), the glow is a 16 px text-shadow on the native rows. Checked f0/f30/f60/f68 at 100%.
Render: npx hyperframes@0.8.184 render -q delivery -f 25 --resolution portrait-4k -o render/vinay_v4_4K.mp4 . (7m27s). Note: the disk hit 0.1 GB free and stalled
  Chrome; freed my placeholder temp PNGs and the HyperFrames extract cache.
