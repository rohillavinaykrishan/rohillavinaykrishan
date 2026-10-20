#!/bin/bash
# Rebuild the sh010 background plate from <project>/edl.json.  Usage: assemble.sh [--proxy]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); PROJ=$(cd "$HERE/../../../.." && pwd)
SUF=""; [ "${1:-}" = "--proxy" ] && SUF="_proxy"
python3 "$HERE/build_plate.py" "$PROJ" "$HERE/bg_plate_raw_1080$SUF.mp4" ${1:-}
python3 "$HERE/build_plate.py" "$PROJ" "$HERE/bg_plate_1080$SUF.mp4" --grade ${1:-}
for f in "$HERE/bg_plate_raw_1080$SUF.mp4" "$HERE/bg_plate_1080$SUF.mp4"; do
  ffprobe -v error -count_frames -select_streams v -show_entries stream=width,height,r_frame_rate,nb_read_frames -of csv=p=0 "$f"
done
"$HERE/sheet.sh" "$HERE/bg_plate_1080$SUF.mp4" "$PROJ/review/plate_v005$SUF.png"
