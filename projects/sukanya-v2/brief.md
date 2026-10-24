# Brief - SUKANYA DILIP DHARIYA credit v2 (ONE final output, ultra HD, the best yet)

Client: SUKANYA DILIP DHARIYA, Sr. Matchmove Artist, DNEG, Street Fighter. Vertical 9:16, 2160x3840 25 fps,
15-20 s (20 s is fine).

## What she asked for (her words via Vinay)
- She LIKES the style of Vinay's FIRST version (review/ref_vinay_v1_sheet.png): the real credit list ROLLING up, so it does not
  look fake - and when HER name comes, it POPS UP with a special effect. "That will look cool."
- Not only one character's fight scene: show AS MANY good-looking fight moments/characters from the trailer as possible.
- Colour team must do something creative; motion animation + motion graphics teams must put in their best work.
- She liked the background music of her previous version (PARALLAX: trailer 141-156 s). She also sent a track:
  source/client_music.mp3 (2:55 instrumental, 136 BPM, D minor, no lyrics; -7.9 LUFS loud master; analysis in
  source/client_music_mood.json). The director decides which serves the piece best (or the best 15-20 s section of her track).
- The director decides everything else - concept, structure, look - aiming for the best result; ultra HD.

## Must
- Real crew roll feel (her name is in the S section: right column, row "SHAHRUKH KHAN | SUKANYA DILIP DHARIYA";
  source/credits.txt holds that section; source/movie.mp4 ~60-66 s shows it). Re-set natively in 4K (never upscale 720p text).
- Her name's pop-up moment = the hero beat, with a special effect, synced to the music.
- Many fight moments / characters (Chun-Li, Ryu, Ken, Guile, Bison, Cammy, Akuma, Dhalsim, Blanka, Vega ...) - premium, smooth,
  layered, beat-synced; no choppy slideshow.
- End card: SUKANYA DILIP DHARIYA - SR. MATCHMOVE ARTIST - STREET FIGHTER - DNEG. No invented facts.
- Different from PARALLAX (her v1) and from Vinay's v4 GROUND TRUTH (in production). No accidental blue cast
  (an intentional, designed palette is fine). No synthetic "ting" SFX; no spoken dialogue in the music.

## Lessons learned (apply)
- Whisper checks must run with VAD OFF (VAD hides vocals under music).
- Trailer active picture is crop=1280:536:0:92; deblock with the grid realigned (pad 4 rows) before upscaling.
- Vertical crops of the 720p trailer are soft: keep footage layers designed (bands, panels, depth, glow, grade) so softness reads as style.
- Credits: native DOM text aligned to the real roll; no blurred underlay showing alone; legible on a phone.
- Render heavy jobs max 2 at a time (4 CPU cores). If an agent hits a usage limit, the producer auto-resumes it.

## Sources
source/movie.mp4, source/trailer.mp4, source/credits.txt, source/client_music.mp3 (+ mood json),
assets_prev/ (sf_logo_silver.png, sf_logo_alpha.png, lineup_restored_2160_r470.png - HD character line-up, trailer transcripts).
