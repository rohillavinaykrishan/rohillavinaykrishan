# Brief - "Sukanya Dilip Dhariya - Street Fighter" filmography credit (ONE final output, best ever)

Client: Vinay Krishan Rohilla, for his friend **SUKANYA DILIP DHARIYA, Sr. Matchmove Artist at DNEG on Street Fighter**.
She is in the crew-thanks reel's credit list. Max 15 s, vertical 9:16, deliver 2160x3840 25 fps (+ <16 MB share copy).

## The key requirement
It must look TOTALLY DIFFERENT from Vinay's video (projects/vinay-credit, delivered v3 "THE SOLVE"), and be even better:
"best motion picture work you've done, better than that". Both will be posted by friends side by side, so they must not
look like the same template with a different name.

## What Vinay's v3 already used (so DON'T repeat as the core idea)
- Concept "THE SOLVE": 2D tracker boxes lock onto names in a scrolling 2-column roll, then the name glides to centre in gold.
- Look: warm red/orange/gold LUT, red grunge poster base, trailer plate at 65-85% behind a vertical roll, ember particles.
- Typography: Inter roll, Oswald header, Bebas Neue title "VINAY KRISHAN / ROHILLA" (ROHILLA gold), the line-up art at the bottom.
- Music: trailer 61.00-76.00 s (incl. the "ROUND ONE!" call), focus-pull low-pass, freeze on the silence, slam on the drop.
- Background shots used: trailer 37-52, 94, 119, 124-126, 136, 142-147.
(See projects/vinay-credit/treatment.md and review/mograph_v003_sheet.png.)

## Lessons from the client on Vinay's versions (still apply)
- No choppy slideshow cuts; layered, smooth, cinematic.
- No synthetic "ting"/chime/drone SFX; one continuous REAL trailer music piece. Accents only subtle/real.
- No muddy accidental blue cast ("it felt blue" was a complaint). A bold intentional palette is fine if it's clearly designed.
- Extreme HD: typography and graphics rendered natively at 4K; never upscale 720p text for the hero.
- Her name highlighted unmistakably; credit list visible; ends on a title card:
  SUKANYA DILIP DHARIYA - SR. MATCHMOVE ARTIST - STREET FIGHTER - DNEG. Don't invent facts.

## Sources
- source/movie.mp4: DNEG crew-thanks reel (720x1280 25 fps, 80 s, no audio). Her name is in the right column at ~62-64 s
  (row: SHAHRUKH KHAN | SUKANYA DILIP DHARIYA).
- source/trailer.mp4: official trailer 1280x720 23.976, 168.75 s, letterboxed (active crop=1280:536:0:92), music + dialogue.
- source/credits.txt: the S-section names around hers (2 columns), transcribed. Row 1 was partly cut off in the source frame, so verify it.
- review/logo_x4.png, review/freeze_x4.png: AI-upscaled credit frames (2880x5120).
- assets_from_vinay/: sf_logo_alpha.png (clean keyed logo), lineup.png (character art with alpha), red_base.png,
  the trailer Whisper transcripts (dialogue spans). Reuse is allowed, but the overall design must differ.
- Tools: 4 CPU cores, no GPU. HyperFrames (incl. Three.js runtime), ffmpeg, Blender (slow: ~30-80 s/frame at 1080p Cycles),
  depth.py (Depth Anything 2.5D parallax, ~0.3 s/frame at 1080p), rembg/SAM roto, Real-ESRGAN for stills (~3 min/frame).
  Google Fonts is reachable. The whole build should fit in about 1.5-2 hours.
