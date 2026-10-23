# sh010 roto v001 - B02 (Balrog glove/arm) and B03 (Blanka) pop-out mattes

Deliverables (2400x900, 25 fps, B02 12 f, B03 11 f; frame N = plate frame N):
- B0x_matte.webm : GRAYSCALE matte video, VP9 lossless (yuv420p), WHITE = subject, black = background. No alpha channel.
- B0x_matte_png/B0x_matte.%04d.png : the same matte as an 8-bit gray PNG sequence (use these for exact values).
- B0x_cutout.webm : plate RGB with the matte as alpha, VP9 + alpha (alpha_mode=1). Decode with `-c:v libvpx-vp9` (ffmpeg's native vp9 decoder drops the alpha).

Method:
1. Tried rembg u2net_human_seg first. It failed on both shots (on B02 it picked up sky/stadium panels and flickered heavily; on B03 it missed Blanka on most frames), so I discarded it.
2. SAM 2 small (tools/vfx/bin/sam_roto.py --frame 5, propagated both ways):
   B02 --point 440,560 940,400 1280,300 1000,800 --neg 600,160 2000,500 (whole Balrog: both gloves, arms, head, torso)
   B03 --point 1100,210 1200,150 1380,300 1000,260 --neg 1300,80 600,600 (whole Blanka)
3. clean.py (in this folder): a 3-frame temporal median, with the neighbouring frames warped to the current frame by Farneback optical flow. The solid core (6 px inside the raw edge) is protected, because both shots whip-pan or dash so fast that a plain median removed 10-30% of the body on some frames. The median therefore only steadies the edge band. Then erode 1 px (3x3 ellipse) and feather with a Gaussian, sigma 2 px.
   IoU of the cleaned matte vs raw SAM: 0.90-0.99 on every frame.

Known issues: on B02 f2 a little sky fringe shows in the gap between arm and head. On B02 f5/f6 the lower-left edge under the near glove (motion-blurred) is ragged. Motion-blurred limbs get fairly hard SAM edges, with no motion blur in the matte.
Check sheet: review/roto_B02_B03_v001.png
