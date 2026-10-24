# sh010 roll v001 (Roll typesetters A + B)

## Transcription (rows above SAMITH SOUMYANATH, movie.mp4 56.0-63.5 s)
- These rows only show at the very start of the window. By 56.04 s the top row is already going under the header mask, so the readable span is RAKESH..SAMEER on frame 56.00.
- A1: frame 56.00, 2x lanczos crops (plus a 3x wide crop for SAIPRASAD). A2: frames 56.08 (RANE..RANJITH) and 56.80 (S BASKARAN..SAMEER), 3x lanczos crops.
- diff: the two passes agree on everything except RAKESH MADHUKAR DEVERE | RUKSHAN ARA NASHRIN, which A2 only sees cut in half by the header mask. That row is dropped.
- rows_verified.txt: 17 names + 1 letter gap (between RANJITH R S and S BASKARAN). Expected ~30; only 17 are readable inside 56.0-63.5. Rows before 56.0 s exist in the movie but are outside the brief.

## Component
- gen_roll.py generates roll.html, roll_rows.json and preview/ (the HyperFrames review project). Edit the generator, not roll.html.
- 2160x3840, master frames at 25 fps, t0 = f0. Visible f0-f260; MG2 takes the rows over at f261.
- Montserrat 500 at 54 px (cap 38), +0.02em, pitch 93, gutter 1083 with a 126 px gap (left cells end at x 1020, right cells start at 1146).
- Motion: speed ramps 70% to 100% over f0-60 (the treatment fallback), then linear 19 px/f, then quad ease-out f243-252 so velocity is continuous. Her row's cap centre is at y 1621.5 at f243 and parks at 1536 at f252.
- Dimming: other rows go 100% to 60% and Ki White to Chalk over f200-232 (linear), then to 22% over f243-252 (expo-out). Her left cell dims from f243. Her name goes Ki White to Saffron over f243-249.
- Fit: cells wider than the 90% action-safe box get scaleX toward the gutter (SAIPRASAD 0.84, SHRIVASTAV 0.97, SOHAN 0.94).
- Verified: snapshots match roll_rows.json to within 1 px. roll_check.png: pitch, gutter and widths line up with the real roll at x4.05.

## Update (coordinator-approved extension before 56 s)
- Pass 1 read 53.00 s. Pass 2 read 52.60 s and 53.60 s. Both agree on RABINARAYAN MISHRA through RAKESH MADHUKAR DEVERE (15 rows). RAKESH is now fully readable on 53.60, so it is restored. "...PRASAD PAL" above RABINARAYAN is cut by the header, so it is dropped.
- rows_verified.txt now has 32 names + 1 gap (33 slots). There are 79 rows in total, and her_row_index = 62 (it was 47).
- Timing is unchanged: her row is at y 1621.5 at f243 and parks at 1536 at f252. The top row is at y 301.5 at f0, so the window (570-3060) is full from f0. The 70% start ramp is kept so the timing stays the same.
