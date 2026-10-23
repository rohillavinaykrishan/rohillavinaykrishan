# Editor v001: plates (ungraded)

- 32 plates in `plates/`: R1-R8, H0, F1-F9 at 2160x904; C1-C6 at 2160x1206; T1-T8 at 482x430 (40 f, MG3 freezes the last frame).
  H.264 crf 10, yuv420p, bt709 tags, 25 fps, no audio. Total size about 57 MB.
- Build with `python3 -I build_plates.py [IDs]`, which reads cues.json (the only timing source). Verify with `python3 -I verify_plates.py`,
  which writes `verify_log.txt` and `edl.json`. All 32 are OK: exact frame counts, size, fps and pix_fmt; every source frame read
  stays inside its shots.json shot; no hidden cuts in any range.
- Prep: crop=1280:536:0:92, pad=1280:540:0:4 (grid realign on top), deblock strong/8, crop=1280:536:0:4, window crop, lanczos, unsharp 5:5:0.4 (0.25 on tiles).
- Retime: speed >= 0.9 uses frame mapping `src_t = src_in + k/25*speed` (23.976 to 25 gives at most 1 duplicate per ~24 f). R1, C1, H0 and the tiles use minterpolate
  mci at fps = 25/speed. R7 uses a frame-blend. C6 ramps 1.0 to 0.2 linearly, using mci at 250 fps and taking the nearest frame. Big-motion guard: source pairs with mean luma diff > 22 are
  hard-stepped to the nearest real frame instead of interpolated (C6 958/959 and 962/963, T2 whip, one T3 pair).
  Reads are clamped at the shot's last frame, and look-ahead frames are padded by cloning the last frame, so no frame from the next trailer shot reaches an interpolator.
- **H0**: the contact is src frame 1222 (50.9676 s); see `H0_contact_proof.png`. The cue src_in of 50.75 was a placeholder. Plain mci at 0.3x ghosted the glove,
  so H0 holds 1222 for 4 f, holds 1223 for 2 f, then runs 0.3x mci from 1224 (the treatment allows a 4-frame freeze on contact). sf045 contains 2 camera cuts that the library
  does not list (1216/1217 and 1221/1222). H0 starts exactly on the second, so it crosses neither. The F8 fallback is not needed.
- R7 range slid back 0.53 src frame (src_in 119.595) so the blend does not pick up 11% of the next trailer shot.
- For the Director (cue choices, not changed by the editor): **T2** (sf031) ends on a whip blur of Ken's back, a poor freeze frame, and sf031 has no clean
  0.64 s span. Consider T2 from sf117 (R2's Ken) or the first 6 frames of sf031 held. **T6** ends with Chun-Li turning away. An earlier src_in (~151.95) ends on her face.
