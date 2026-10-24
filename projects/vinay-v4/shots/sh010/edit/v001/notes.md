# editor v001 - sh010 (vinay-v4 GROUND TRUTH)

## PLATE (ready - layout / roto / colorist start here)
`projects/vinay-v4/shots/sh010/edit/v001/plate/plate.%04d.png`: 52 frames, 1280x536 RGB PNG.
plate.0001 = src frame 2982 = s0 ... plate.0052 = src frame 3033 = s51  (plate.N = s(N-1) = src 2981+N).
Command: `ffmpeg -i source/trailer.mp4 -vf "select='between(n,2982,3033)',crop=1280:536:0:92" -vsync 0 -start_number 1 plate/plate.%04d.png`
Boundary check (frame-diff + HSV histogram correlation at 320 px):
- Hard cut into the beach shot is between src 2980 and 2981 (mean abs diff 100.5, hist corr 0.47). 2982 is the 2nd frame of the shot -> no neighbour frame.
- The beach shot continues to src 3067 (next hard cut 3067->3068, diff 120). 3033 is mid-shot (a whip, diff 39.8, hist corr 0.98) -> no neighbour frame.
- plate.0001 matches src 2982 (diff 1.4 vs 16-24 for 2981/2983); plate.0052 matches src 3033 (1.4 vs 26-40).
- Visual contact sheet: work/plate_sheet.png, boundaries: work/bnd_sheet.png.

## CREDITS
`credits_src.mp4`: source/movie.mp4 frames 1685-1753 (67.40-70.16 s), 69 frames, 720x1280, 25 fps, 2.76 s, H.264 crf 10, no audio.
`ffmpeg -i source/movie.mp4 -vf "select='between(n,1685,1753)',setpts=N/25/TB" -an -r 25 -c:v libx264 -crf 10 -preset slow -pix_fmt yuv420p credits_src.mp4`
Frame 0 is identical to `-ss 67.40` (diff 0.0).

## ROW TRACK
`row_track.json`: per frame y (cap-height centre, caps 10 px tall), x extents of his name and of the partner name, in src px and in x3 canvas px.
Method: OpenCV template match (his name from f40), parabolic subpixel, scores 0.92-1.00 on every frame. Script: work/row_track.py. Check: work/row_check.png.
- His name: x 377-554 (cx 465.5), static in x. Partner (VAMSI KRISHNA EADALA): x 168-346. Row pitch 23 px.
- y: 827.4 (f0) -> 629.5 (f40, 69.00 s) -> 604.4 (f45, 69.20 s) -> 486.7 (f68). About -5.0 px/frame, nearly linear (quadratic fit residual 0.23 px).
- It crosses the frame centre (y 640) at f38 (src 68.92 s). Full brightness on all 69 frames (no fade from the roll's mask).

## CUE AUDIT (cues.json vs bed_112.10-127.10.wav vs frame plan). Script: work/cuecheck.py, data: work/bed_analysis.json
OK:
- The bed is 15.000 s and starts at exactly trailer 112.100 (FFT cross-correlation against source/trailer.mp4).
- Every cue's src time equals 112.10 + f/25. The acts tile 0-374 with no gap or overlap (69+52+16+32+52+52+2+100 = 375).
- The TRACK/FINAL/BREAKDOWN passes are 52 frames each, matching the 52 plates. Landing on s4 = f169+4 = f173. The x1.30 / 2808x1176 / CX clamp 493-787 numbers check out.
- The near-silence is real: f159-165 are all <= -30 dB RMS. The dip f137 is -30 dB.
- Attacks at 5 ms resolution: f69 (68.1), f113 (112.3), f121 (121.0 onset), f141 (140.4), f173 (172.9; peak 173.75), f251 (250.8), f275 (275.1), f291 (290.6). All on target or within 1 frame.
Inconsistencies:
1. HERO f173 "+21 dB in one 40 ms bin, most violent transient" is not what the bed shows. On the 40 ms frame grid, f172->f173 is only +3.7 dB. The +21 dB is the whole climb from the silence floor (f163 -34.0 dB) to f173 (-12.9 dB) over ~10 frames. There is a real attack at f172.9 (+8.5 dB in 15 ms), so landing on f173 is still right. But the steepest transients in the window are f141 (+17 dB/15 ms, +9.1 dB per frame bin) and f82.6 (+15 dB/15 ms). Fix the description, not the timing.
2. f304 (STREET FIGHTER · DNEG): the attack is at f301.1 (onset detector f302.25), peak f305.4. The cue sits about 2-3 frames after the attack. Suggest f302.
3. f81 (track density step): the strongest attack is at f82.6 (+15 dB/15 ms); f81 itself is weak (onset 0.5x p90). Suggest f82 or f83.
4. f208 (LOCKED tag): a soft hit, attack at f206.9 (onset 207.5), peak 209.3. Within +/-1, acceptable.
5. TITLE "loudest sustained hit, -10.9 dB at f275": on the frame grid f275 is -11.8 dB, and -10.9 is at f277. f291/f292 are as loud (-11.0/-11.1), with a higher 5 ms peak (-6.5 vs -7.5 dB). f275 is still a strong attack exactly on frame (275.1) and is the right title cut. It is just not uniquely the loudest.
6. Plate times: cues "src_time [124.376, 126.502]" are frame *start* times rounded. Exact: 2982 starts at 124.3743, 3033 starts at 126.5013 and ends at 126.5430. Treatment 3.1 calls 124.374-126.543 the whole shot (52 fr). In fact the shot runs 2981-3067 (124.333-127.961); 126.543 is a whip, not a cut. The plate choice is valid (no neighbour frames). Layout may use 2981 and 3034+ as extra solve context if needed.
7. Credits: cues row_y_at_69.0 = 630, measured 629.5 (OK). Treatment says "y ~607 at 69.20", measured 604.4 (2.6 px off, harmless). The row crosses the centre at 68.92 s, slightly before the treatment's "69.0-69.2".
8. Naming: cues calls f273-274 "HOLD s51 stack", treatment section 7 animates a 2-frame fold to centre. The EDL follows the treatment (fold on s51).

## EDL
`projects/vinay-v4/edl.json`: 8 cuts c001-c008 per treatment sections 6-7, contiguous, 375 frames, with sources, moves, transitions and music sync.
Assembly (edit_v###.mp4 / assemble.sh) waits for the department outputs.
