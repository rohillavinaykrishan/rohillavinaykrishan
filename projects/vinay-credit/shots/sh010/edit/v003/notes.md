# sh010 edit v003 - background plate (treatment v3 sec. 6 / 11.1)
- EDL: ../../../../edl.json (timeline, cuts A-J with src in/speed/crop/transition, opacity curve, roll/lock/freeze/slam/title frames).
- Rebuild: `./assemble.sh` (raw + graded + ffprobe + review/plate_v003.png), `./assemble.sh --proxy` for 540x960. ~10 min at 1080 on a loaded machine.
- build_plate.py: per clip `-ss` -> active crop -> 302x536 vertical crop (B pans 380->720) -> setpts/speed -> minterpolate mci to 25 fps
  -> lanczos 1080x1920 -> push-in (A 1.05, G 1.08) -> unsharp 5:5:0.45 luma -> [--grade: per-shot trim] ; xfade chain centred on the beat frames;
  I frozen on 299 via tpad (299-306); J hard cut at 307 + 4-frame white flash (0.85/0.47/0.26/0.14) -> pale gold through the LUT.
- Graded = trims (A eq=gamma=1.45:contrast=1.05, G eq=gamma=0.85) + lut3d color/v001/warm.cube + color/v001/finish_filter.txt (luma-only grain).
- Speed/in deviations from the treatment (kept every clip + handles inside its own trailer shot, scdet-measured): A 0.68x, B 0.90x in 37.82 (trailer's internal cut 38.29 lands on beat frame 38), C in 39.74, D 0.82x, E in 50.20, F 0.62x, G 0.48x.
- QC: 375 frames both files; raw YDIF 300-306 ~0.005 (true freeze); graded min YAVG 19.9 (no black frames); mean V-U > 0 on every frame (min 8.9) => no blue cast.
- Known: graded freeze frames carry live temporal grain (YDIF ~3.4). bg_plate_1080.mp4 is 179 MB (CRF 14 + grain). Some mci warping in J's fast motion, masked by blur/opacity.
