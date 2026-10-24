# Auto QC: Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_30s_4K.mp4

File: `/home/user/rohillavinaykrishan/projects/vinay-30s/deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_30s_4K.mp4`  
Run: 2026-10-24 03:43 (container time), 19 s, `auto_qc.py` (expect 2160x3840 @ 25 fps, 750 frames)

# VERDICT: FAIL

| Gate | Result | Detail |
|---|---|---|
| black frames | **FAIL** | f0-19 (0.00-0.80 s, 20 fr), f237 (9.48 s), f357-364 (14.28-14.60 s, 8 fr) |
| R >= B (no blue cast) | **FAIL** | 106 frames with B > R; worst f150 R-B -38.6 |
| frozen frames | **WARN** | f2-19 (0.08-0.80 s, 18 fr), f357-364 (14.28-14.60 s, 8 fr), f402-403 (16.08-16.16 s, 2 fr), f426-427 (17.04-17.12 s, 2 fr), f447-448 (17.88-17.96 s, 2 fr) ... (+17 more) (check they are intended holds) |
| names | MANUAL | 1 name(s) to read at 100% |
| near-still spans | INFO | f0-19 (0.00-0.80 s, 20 fr), f389-390 (15.56-15.64 s, 2 fr), f496-520 (19.84-20.84 s, 25 fr), f523-528 (20.92-21.16 s, 6 fr) ... (+6 more) |
| contact sheet | INFO | auto_qc_sheet.png |
| specs | PASS | 2160x3840 25 fps CFR, 750 fr, 30.000 s, starts 0 |
| loudness | PASS | I -14.0 LUFS, TP -1.9 dBTP, LRA 2.7 LU |

## 1. Specs (ffprobe)

| | |
|---|---|
| Video | h264 High, yuv420p, bt709/bt709/bt709 tv |
| Size / fps | 2160x3840, r 25/1, avg 25/1 |
| Frames (packets) | 750; pts deltas min 40.00 ms, max 40.00 ms |
| Video start / duration | 0.000 s / 30.000 s |
| Audio | aac LC, 48000 Hz, 2 ch, 316 kb/s, start 0.000 s, duration 30.000 s |
| File | 155.2 MB, 41.4 Mb/s |

## 2. Loudness (ebur128, true peak)

Integrated **-14.0 LUFS** (target -14 +/- 0.5), LRA 2.7 LU, true peak **-1.9 dBTP** (max -1).

## 3. Black / frozen frames

Decoded 750 frames at 360x640. Darkest frame: f0 (mean 6.3/255).

- Black (>=98% of pixels with luma < 0.05, like blackdetect pix_th): f0-19 (0.00-0.80 s, 20 fr), f237 (9.48 s), f357-364 (14.28-14.60 s, 8 fr)
- Frozen (frame ~= previous, mean abs diff < 0.05/255 at 360x640): f2-19 (0.08-0.80 s, 18 fr), f357-364 (14.28-14.60 s, 8 fr), f402-403 (16.08-16.16 s, 2 fr), f426-427 (17.04-17.12 s, 2 fr), f447-448 (17.88-17.96 s, 2 fr), f497-512 (19.88-20.52 s, 16 fr), f517-518 (20.68-20.76 s, 2 fr), f622-633 (24.88-25.36 s, 12 fr), f651-652 (26.04-26.12 s, 2 fr), f669-685 (26.76-27.44 s, 17 fr), f694-695 (27.76-27.84 s, 2 fr), f699-700 (27.96-28.04 s, 2 fr), f703-704 (28.12-28.20 s, 2 fr), f708-709 (28.32-28.40 s, 2 fr), f713-714 (28.52-28.60 s, 2 fr), f718-719 (28.72-28.80 s, 2 fr), f723-724 (28.92-29.00 s, 2 fr), f728-729 (29.12-29.20 s, 2 fr), f733-734 (29.32-29.40 s, 2 fr), f737-738 (29.48-29.56 s, 2 fr) ... (+2 more)
- Near-still (diff < 0.2/255; slow end cards, embers, grain): f0-19 (0.00-0.80 s, 20 fr), f389-390 (15.56-15.64 s, 2 fr), f496-520 (19.84-20.84 s, 25 fr), f523-528 (20.92-21.16 s, 6 fr), f569-582 (22.76-23.32 s, 14 fr), f587-598 (23.48-23.96 s, 12 fr), f605-616 (24.20-24.68 s, 12 fr), f622-634 (24.88-25.40 s, 13 fr), f642-664 (25.68-26.60 s, 23 fr), f688-749 (27.52-30.00 s, 62 fr)
- Smallest consecutive-frame change: 0.002/255 at f448; median 0.95/255.

## 4. Blue cast (per-frame mean R >= B - 0)

Whole clip mean R 39.8, G 32.8, B 33.0. Frames with B > R: **106** of 750 (f0-19 (0.00-0.80 s, 20 fr), f122-197 (4.88-7.92 s, 76 fr), f236-237 (9.44-9.52 s, 2 fr), f357-364 (14.28-14.60 s, 8 fr)).

Worst 5 frames: f150 R-B -38.6 (R 12 G 21 B 50), f151 R-B -38.5 (R 12 G 21 B 50), f149 R-B -38.3 (R 11 G 21 B 50), f148 R-B -38.2 (R 12 G 21 B 50), f152 R-B -38.2 (R 12 G 21 B 50).

## 6. Names (MANUAL spelling check; no OCR in this toolset)

- [ ] `VINAY KRISHAN ROHILLA`: read it at 100% on the 4K frames (spelling, every occurrence).

## 7. Contact sheet

`/home/user/rohillavinaykrishan/projects/vinay-30s/shots/sh010/comp/v001/check/final4k/auto_qc_sheet.png` (12 frames at 360x640).
