# sh010 color v003 - v3 re-delivery (new inputs)
Inputs: mograph/v003/render/sh010_mograph_4K.mp4 (2160x3840, 25p, 375 fr, BT.709) + sound/v004/mix_master.wav (15.000 s, -14.0 LUFS, -1.5 dBTP).
Finishing: NONE (no LUT, no re-grade, no re-master). Same process as color/v002.
4K: libx264 High CRF 15 slow/film, keyint 50, yuv420p, BT.709 tv, AAC 320k 48k, +faststart, 375 frames. 3m46s, 166.3 MB.
Share: 1080x1920 lanczos, 2-pass 7200k (maxrate 11M), AAC 192k -cutoff 20000, +faststart. 58s, 13.7 MB.
QC: both 375 fr, v+a start 0, 15.000 s. 4K -14.0 LUFS / -1.4 dBTP; share -14.1 LUFS / -1.4 dBTP (both pass <= -1.0, no audio rework).
SSIM: 4K 0.9919, share 0.9813 (vs lanczos-downscaled source). Sheet: review/deliver_v3.png
