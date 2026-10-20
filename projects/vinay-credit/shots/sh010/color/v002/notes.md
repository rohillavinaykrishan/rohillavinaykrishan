# sh010 color v002 - final conform + delivery v3
Inputs: mograph/v002/render/sh010_mograph_4K.mp4 (2160x3840, 25p, 375 fr, BT.709) + sound/v003/mix_master.wav (15.000 s).
Finishing: NONE. Not re-graded and no LUT (the plate is already graded; a LUT would turn the ivory type gold). Source checked first: YMAX 246, YMIN 0, mean Y 44, which is the intended dark fire-lit look. No re-master.
4K: libx264 High, CRF 15, preset slow, tune film, keyint 50, yuv420p, BT.709 tv-range tags, AAC 320k 48k, +faststart, -frames:v 375. Took 5m13s. Size 169.9 MB.
Share: 1080x1920 lanczos, 2-pass at 7200k (maxrate 11M), AAC 192k, +faststart. Took 1m11s. Size 13.6 MB.
QC: both 375 frames, v+a start 0.000, duration 15.000; -14.0 / -14.1 LUFS, true peak -1.0 / -0.9 dBFS, LRA 3.3.
SSIM vs source: 4K 0.99, share (vs lanczos-downscaled source) 0.98. Sheet: review/deliver_v3.png
Logs: encode_4K.log, encode_share.log (empty = no errors)
