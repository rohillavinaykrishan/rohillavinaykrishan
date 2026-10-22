# sh010 restore v001 - line-up for the CREDITS act (director notes 4, 15)
Output: lineup_restored_2160.png - 2160x900 RGBA = assets_prev/lineup.png src rows 560-1760, 0.75x INTER_AREA. Place at y 2940-3840.
1. restore.py assets_prev/lineup.png --no-upscale --face-strength 0.6 (3m07s, 10 frontal faces) and --face-strength 0 (A/B).
2. Per-face pick (work/select.py): 0.6 kept for Ryu, Ken, Guile, Cammy, Dhalsim-style bearded fighter, megaphone fighter, blond fighter;
   0 kept for M. Bison (0.6 invents a blue eye under the cap shadow), Akuma (0.6 paints a human eye on the creature face), cap fighter (garbled 3/4 face).
   Chun-Li is a profile, skipped by the detector, so she is untouched.
3. work/finish.py: shadows lifted toward Umber #2A211A (weight 0.7, luma<0.32, saturated costume colour masked out: mean change 0.09 levels on costumes),
   top alpha smoothstep 0->1 over 300 px.
Source check: lineup.png == review/logo_x4.png rows 3360-5120 with the credit names and DNEG painted out. A 617-frame temporal median of movie.mp4
(line-up static 1.6-79 s) was only marginally cleaner and keeps the DNEG mark, so lineup.png was used.
Known: bodies keep the source macro-blocking (Bison coat, Chun-Li arm), so use it small/downscaled only, as planned.
