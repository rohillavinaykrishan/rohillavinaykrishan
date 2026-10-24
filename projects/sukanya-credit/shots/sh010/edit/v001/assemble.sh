#!/usr/bin/env bash
# Rebuild the sh010 background plate from <project>/edl.json.  usage: assemble.sh [work_dir]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJ="$(cd "$HERE/../../../.." && pwd)"
WORK="${1:-$HERE/_work}"
mkdir -p "$WORK"
vfx-python "$HERE/build_plate.py" "$PROJ" "$HERE" "$WORK"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_read_frames -of compact "$HERE/bg_plate_raw_1080.mp4"
