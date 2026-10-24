# Brief v3 - "Vinay Krishan Rohilla - Street Fighter" filmography credit (ONE final output, best quality)

Client: Vinay Krishan Rohilla, **Sr. Matchmove Artist at DNEG on Street Fighter**. He wants to show the world he worked on the film.
Max 15 s. Vertical 9:16 (WhatsApp status / Instagram Reels / LinkedIn). Deliver 2160x3840.

## Client feedback on v1/v2 (must fix)
- "Poorly mixed": v1/v2 hard-cut between trailer montage, credit reel and title card. He wants LAYERS:
  the trailer footage playing in the BACKGROUND, slightly transparent / dimmed, and the credit list with
  his name highlighted coming ABOVE it. "Or something similar, any creative idea" - be super creative.
- "Video was feeling blue": the trailer has a lot of blue/teal neon shots. Grade warm (Street Fighter
  red / orange / gold, deep blacks). Avoid or re-grade blue shots.
- "Extreme HD": v1/v2 upscaled a 720p credit reel and 302-px-wide crops of a 720p trailer - soft.
  => REBUILD the credit roll as crisp vector typography rendered natively at 2160x3840 (HyperFrames),
  do not upscale the 720p credit video for the foreground. Background footage may be soft (it is dimmed/blurred bg).

## Sources (source/, never modify)
- source/movie.mp4: DNEG crew-thanks reel, 720x1280 25fps, 80 s, NO AUDIO. Street Fighter logo top, "Thanks to our
  talented teams!", 2-column alphabetical crew names scroll up over red key art with the character line-up at bottom,
  DNEG logo at end. His name is in the right column at ~68-70 s.
- source/trailer.mp4: official trailer, 1280x720 23.976fps, 168.75 s, letterboxed (active picture crop=1280:536:0:92),
  has music + dialogue. Logo card at ~154.7 s. Dialogue "You did that" at ~157.3 s. Shot cuts (s): 21.0 23.0 28.6 29.9
  32.7 33.7 35.5 36.7 37.5 39.6 40.9 41.9 43.0 49.3 49.6 52.0 52.8 56.9 58.9 93.9 96.0 97.3 98.2 99.1 108.7 109.4 118.0
  118.8 122.9 123.7 124.3 128.0 133.2 135.0 135.7 137.3 141.9 146.1 147.9 148.7 157.1 158.2 159.2 160.7 161.2 163.7 166.0
  Warm action shots seen: 36.9 arena fight, 38.5, 40.0 bald fighter punch, 41.2 flying blonde hair, 50.6/52.0 boxer vs Ken,
  119.4 Bison (red uniform), 124.0 scream (orange), 126.0 desert fight, 136.0 jump kick arena (golden light), 143 Ryu fist (blue - regrade).
- source/credits.txt: the crew names around his, transcribed (two columns, '|' separator, blank line = letter gap).
- review/freeze_x4.png (2880x5120 AI-upscaled credit frame), review/logo_x4.png (AI-upscaled logo/key-art frame, 2880x5120):
  use for the Street Fighter logo and character line-up art (crop/key out) at high res.
- Previous versions for reference only: render_credit.py, render_v2.py, deliver/*v2*.

## Must show
- VINAY KRISHAN ROHILLA (highlighted, unmistakable) - SR. MATCHMOVE ARTIST - STREET FIGHTER - DNEG.
- Do not invent facts (no release year, no other roles).

## Tools / constraints
4 CPU cores, no GPU. Free tools only (no Runway/ElevenLabs). Real-ESRGAN = ~3 min per 720x1280 frame at 4x: stills only.
SFX kit already in sfx/ (boom, downlifter, glitch, impact, reverse, riser, shimmer, swipe, tape-stop, whoosh).
Fonts: Inter / Inter Display installed; Google Fonts may be reachable for HyperFrames (check). github raw is blocked.
