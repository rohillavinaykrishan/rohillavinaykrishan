# Brief - Vinay Krishan Rohilla credit v4 "the best one" (ONE final output)

Client: VINAY KRISHAN ROHILLA, **Sr. Matchmove Artist at DNEG on Street Fighter**. 15 s max, vertical 9:16, 2160x3840 25 fps
(+ <16 MB share copy). His name is in the DNEG crew-thanks reel (source/movie.mp4, right column ~68-70 s,
row "VAMSI KRISHNA EADALA | VINAY KRISHAN ROHILLA"); credits around it in source/credits.txt.

## Why v4
We made him v3 "THE SOLVE" and his friend Sukanya "PARALLAX". He loves hers and now feels his is poor.
v4 must be clearly BETTER than PARALLAX and DIFFERENT from both. This is the flagship.

## Already used - do not repeat as the core idea
- v3 THE SOLVE (projects/vinay-credit): flat 2-column roll over a warm red/gold trailer plate, 2D tracker boxes lock on his name,
  gold name glides to centre, Bebas title, line-up art. Music trailer 61-76 s (ROUND ONE!). Sheet: review/prev_vinay_v3_sheet.png
- PARALLAX (projects/sukanya-credit): silver B&W + lime, names floating in 3D (CSS 3D camera), point-cloud Chun-Li face,
  snap-flat solve, Bodoni title, chrome logo. Music trailer 141-156 s. Sheet: review/prev_sukanya_sheet.png

## Producer's big idea (director may improve on it)
"REAL MATCHMOVE": his actual craft. Take a real trailer shot with camera movement, SOLVE THE CAMERA (COLMAP, free),
and integrate his name as a 3D element INSIDE the movie world (e.g. carved/lit lettering on the arena floor, a hanging
fight-banner, or neon on a wall), locked to the moving camera like a real VFX shot, with shadows/occlusion/light wrap.
Show the "making-of" honestly and cinematically: track points appear on the plate -> solve -> CG name lands in the shot.
Optionally a short breakdown wipe (plate / tracking / CG / final) - the language of VFX reels that matchmove artists use.
Then the credit list moment and a title card that beats PARALLAX's.

## Client rules (from earlier feedback)
- Layered, smooth, cinematic; no choppy slideshow. Real trailer music only, no synthetic tings/drones.
- No accidental blue cast; a designed palette (different from red/gold-only and from silver+lime).
- Extreme HD: graphics/type native 4K. His name unmistakable. Ends on: VINAY KRISHAN ROHILLA - SR. MATCHMOVE ARTIST -
  STREET FIGHTER - DNEG. No invented facts.

## Sources / assets
source/movie.mp4, source/trailer.mp4 (1280x720 23.976, letterbox crop=1280:536:0:92), source/credits.txt,
review/logo_x4.png, review/freeze_x4.png, assets_prev/ (sf_logo_alpha.png, sf_logo_silver.png, lineup.png, trailer transcripts).
Dialogue-free music windows already found: 61-76 (used, has "ROUND ONE!"), 141-156 (used). Whisper's whole-trailer pass misses
short shouts - re-transcribe any candidate clip. Reusing a window is allowed only if cut differently and it truly serves the piece.
Tools: 4 CPU cores, no GPU. COLMAP (~40 s per 30 frames at 640x360), Blender 5.2 (Cycles CPU: simple text/plane scenes at
1080p ~5-20 s/frame with low samples; render CG as RGBA passes and comp in ffmpeg/HyperFrames), HyperFrames, depth.py, SAM 2 roto,
Real-ESRGAN for stills. Budget ~2-3 h wall clock; heavy jobs max 2 at a time.
