# sh010 edit v001 (build plan task 1)
Rebuild: `./assemble.sh [work_dir]` (reads ../../../../edl.json, runs build_plate.py; ~2 min).
- Slowed cuts: ffmpeg crop (exact=1) at 302x536 -> setpts -> minterpolate mci to 25 fps -> cv2 Lanczos to 1080x1920 (pixel-centre mapping = swscale).
- P7/P8 sync: trailer frame floor((141 + f/25) * 23.976); frame 270 = 151.777 (crouch), 271 = 151.818 (the trailer's cut to Chun-Li).
- Transitions centred on the cut frame (luma wipe 47-52, dissolves 83-86, 113-116, 192-197, 226-233), flash 151-152 (#F4EFE6 screen 40/20%), flare 323-326 (20/50/50/20%), hard cut 271.
- P4 = shots/sh010/roto/v001/p4_parallax.mp4 (36 fr), first frame held for 2 dissolve frames.
- Source fixes vs cues.json (cues ranges crossed trailer cuts): P1 30.62 @0.39x, P2 in 32.78, P3 108.74 @0.50x, P5 147.95 @0.37x, P6 in 118.02. See edl.json `edit_fix`.
- P8 / hero CX 769 = crop x 618, which is what roto's hero_1080.png actually used (ffmpeg yuv420p crop rounds x 619 down). hero_1080.png = trailer frame 3642 (pts 151.902) = plate frame 273; plate frame 271 = trailer 151.818 -> hero_f271_1080.png.
- Frame 324 = trailer 153.96, which is the trailer's own title-flare frame (153.945); sits under the ivory flare peak.
- Credits row 1 verified at movie.mp4 57.5-58.5 s (2x crops): SAMITH SOUMYANATH | SIDDHANT SUNIL SONAWANE is correct (credits_row1_check_58.0s.png).
