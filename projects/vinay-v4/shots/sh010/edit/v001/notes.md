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
