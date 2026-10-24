# sh010 edit v001: Editor B (Super Art plates C00, B01-B08)

Timing comes from director/v001/cues.json only. Shot ranges were checked against library/streetfighter-trailer/shots.json.

## Rebuild
    python3 plan_B.py edl_B.json     # frame map (asserts every pick is inside one librarian shot)
    ./build_B.sh [ID ...]            # plates/<ID>.mp4, 2400x900, 25 fps, x264 crf10 yuv444p, ungraded
Scratch goes to the session scratchpad and is deleted after hand-off. Rebuilding C00/B01 re-runs minterpolate (~1 min).

## Pipeline
crop 1280:536:0:92 -> pad 4 rows at the TOP -> deblock strong/8 -> crop back. This realigns the grid: the crop starts at y92 = 8*11+4.
- C00/B01: minterpolate mci/aobmc/bidir/vsbmc at 24 sub-steps per source frame (input frames 3446-3456, inside sf126). Then pick the positions from edl_B.json.
- B02-B08: nearest-source-frame conform, src_t = src_in + k/25*speed (speeds 1.0-1.146). No duplicated frames.
- Then: lanczos 2400x1005 -> crop 2400x900 (y=52; B02/B03 y=0, B08 y=10 to keep heads and Blanka in frame) -> unsharp 5:5:0.4.

## Checks
- Frame counts: C00 18, B01 16, B02 12, B03 11, B04-B08 10 each. All equal f_out-f_in, verified with ffprobe -count_frames.
- No plate crosses a trailer cut: the source picks are asserted inside the librarian shot ranges, and scdet inside every plate peaks at 8.8 (B02's punch motion).
- Contact: plate B01 frame 0 = master f261 = source frame 3452 (143.977). PSNR 54.3 dB vs the processed source frame, against 23.6/27.2 dB for frames 3451/3453. minterpolate is bit-exact at integer positions. See contact_proof.png.

## Known issues
- B01: the cue src_out 144.06 leaves only ~2 source frames after contact. A literal linear 100%->20% ramp over f261-271 would need about 0.24 s (to ~144.22, still inside sf126). So v001 uses a geometric decay: 100% at f261, about 20% by f263-264, then it settles into the freeze (f272-276 frozen). If the Director wants the longer ramp, change src_out in make_cues.py and rebuild B01 (~1 min).
- C00 f260 (src 3451.67) has mild optical-flow doubling on Ken's knuckle edge. It reads as motion blur. No limb warping elsewhere.
- Ungraded. B04 is very dark and B07/B08 are blue/magenta, so they are for the colorist's band.cube and R>=B check (treatment §12 lists swaps).
