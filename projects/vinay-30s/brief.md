# Brief - VINAY KRISHAN ROHILLA 30 s credit (brand-new design, ONE 4K master)

Client: VINAY KRISHAN ROHILLA, Sr. Matchmove Artist, DNEG, Street Fighter. 30.0 s, vertical 2160x3840, 25 fps.
Deliver ONLY the 4K master. Times to the client in IST.

## Ask
A completely NEW 30-second design - not a longer cut of any earlier piece - and the best one yet.
Must differ from all five earlier pieces (sheets in review/):
- Vinay v1/v2 (hard-cut montage + freeze zoom), v3 THE SOLVE (red/gold flat roll + 2D trackers),
  v4 GROUND TRUTH (COLMAP solve, 3D name monument on the beach, VFX breakdown, sand/pink),
- Sukanya PARALLAX (silver B&W + lime, 3D floating names, point-cloud face),
- Sukanya SUPER ART (plum/saffron, rolling credits, fighting-game Super Art name pop, beat band).
Quality bar: review/client_quality_reference.jpg (ultra-crisp, rich colour, glow, unmistakable name).
With 30 s there is room for a real arc: more fight characters/moments, a bigger hero beat for his name, and a
strong ending card (VINAY KRISHAN ROHILLA - SR. MATCHMOVE ARTIST - STREET FIGHTER - DNEG). No invented facts.

## Music: director decides
No single 30 s dialogue-free window exists in the trailer. Options: stitch clean sections on a beat
(see library audio_map.json: clean_music_windows 63.89-82.70 [sung line at 79-81], 144.27-156.54 [chant]; other music
spans with dialogue gaps), sung lyrics are fine, SPOKEN dialogue is not. Whisper checks with VAD OFF. Real music only, no synthetic SFX.

## Assets
- Shot library (use it, don't re-scan): /home/user/rohillavinaykrishan/library/streetfighter-trailer/ (shots.json, heroes.png,
  audio_map.json, sheets/, stills/).
- source/movie.mp4 (crew roll; his row "VAMSI KRISHNA EADALA | VINAY KRISHAN ROHILLA" ~68-70 s), source/credits.txt (V section).
- source/trailer.mp4 (active picture crop=1280:536:0:92; deblock with pad=1280:540:0:4 [top] to realign the 8x8 grid).
- Reusable from earlier projects: vinay-v4 camera solve (layout/v001), restored line-up (assets_prev/), credit-roll code
  (sukanya-v2/shots/sh010/roll/v001/gen_roll.py), Super Art/HUD/title code in sukanya-v2 and vinay-v4 mograph folders.

## Lessons (apply)
4K native type; legible on phone; no blurred underlay alone; no blue cast unless designed; R>=B QC; Chrome needs yuv420p video;
heavy jobs <= 2; keep disk use small (H.264 crf 10 intermediates, delete scratch); comp lead is the only 4K renderer.
