# director v001 - vinay-v4 "GROUND TRUTH" treatment data
- Treatment: projects/vinay-v4/treatment.md. Timing source of truth: cues.json.
- Music: trailer 112.10-127.10 (Whisper clip pass 110-132: last word ends 112.03, next starts 127.18).
- Hero plate: trailer src frames 2982-3033 (124.376-126.502), beach fight. COLMAP: 37/37 registered, 0.60 px (960 px); 37/37, 0.603 px (640x268, 133 s).
  Needs relaxed mapper options (scripts/map.sh, scripts/cm3.sh). Stock automatic_reconstructor fails on every trailer shot.
- Lookdev: scripts/lookdev.py (COLMAP cam -> Blender, 24-31 s/frame at 2160x904 16 spp), scripts/title.py (title monument proxy, ~11-15 s at 540x960).
- Other candidates (cm2_*, cm3_*) failed or were degenerate; kept as evidence.
