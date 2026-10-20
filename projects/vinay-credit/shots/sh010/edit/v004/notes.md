# sh010 edit v004 - background plate (supervisor note 3 + team-lead QC a/b)
- Rebuild graded: `python3 build_plate.py <proj> bg_plate_1080.mp4 --grade` (~5 min); `./assemble.sh` also builds raw + sheet. EDL: ../../../../edl.json (v004); v003 EDL snapshot in ../v003/edl_v003.json.
- Leaks B@25 (left), E@120 (right), G@168 (top-right): fadewhite replaced by a 6-frame fade dissolve + a radial side leak (screen blend, #FFD6A0, before the LUT),
  envelope 0.58*max(0,1-|f-beat|/6)^1.3, ramping over 5 frames each side with the peak exactly on the beat frame. Plate mean luma at 23-25: 25/27/30 (v003: 144/143/124).
- J: the trailer has its own cut at 146.897 s. J is now 146.104-146.840 at 0.40x (frames 307-353), then holds frame 353 through 374. Max YDIF 325-374 = 5.6 (v003: 35.9 at 334).
- Unchanged: trims, LUT, finish_filter, freeze 299-306 (YDIF 0.8 = grain only), 307 hard cut + white flash, 375 frames.
