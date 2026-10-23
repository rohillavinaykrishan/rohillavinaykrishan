#!/usr/bin/env bash
# vinay-30s sh010 comp v001 - rebuild the master from upstream files and render.
#   ./comp.sh build          sync MG1-3 into master/ (tools/build_master.py) + lint
#   ./comp.sh proxy          2160 layout rendered at 1080 (--resolution portrait) -> 540x960 proxy + audio
#   ./comp.sh half a|b       native 2160x3840 HyperFrames render of f0-364 (a) or f365-749 (b), crf 8
#   ./comp.sh join           lossless concat of the halves -> render/vinay30_4K_picture.mp4 (750 f, no audio)
#   ./comp.sh deliver        deliver_4k.sh (x264 crf 12 film yuv420p, AAC 320k) -> deliver/ + render/vinay30_4K.mp4
#   ./comp.sh posters        f374 + f749 4K PNGs from the joined picture
set -euo pipefail
PRJ=/home/user/rohillavinaykrishan/projects/vinay-30s
V=$PRJ/shots/sh010/comp/v001
WAV=$PRJ/shots/sh010/sound/v001/master.wav
R=$V/render
OUT=$PRJ/deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_30s_4K.mp4
mkdir -p "$R"
cd "$V/master"

case "${1:-}" in
  build)
    python3 "$V/tools/build_master.py"
    npx hyperframes lint 2>&1 | tail -1 ;;
  proxy)
    python3 "$V/tools/build_master.py"
    npx hyperframes render . --resolution portrait -q draft -f 25 -o "$R/_proxy1080.mp4" --quiet > "$R/proxy_render.log" 2>&1
    A=$WAV; [ -f "$A" ] || A=$PRJ/shots/sh010/director/v001/audio/bed_vinay30_v001.wav
    ffmpeg -v error -y -i "$R/_proxy1080.mp4" -i "$A" -map 0:v:0 -map 1:a:0 -vf scale=540:960:flags=lanczos \
      -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$R/vinay30_proxy540.mp4"
    rm -f "$R/_proxy1080.mp4" ;;
  half)
    h=${2:?a|b}
    cd "$V/half_$h"
    npx hyperframes render . -q delivery --crf 8 -f 25 -o "$R/half_$h.mp4" > "$R/render_4k_$h.log" 2>&1 ;;
  join)
    printf "file '%s'\nfile '%s'\n" "$R/half_a.mp4" "$R/half_b.mp4" > "$R/halves.txt"
    ffmpeg -v error -y -f concat -safe 0 -i "$R/halves.txt" -map 0:v:0 -c copy -an "$R/vinay30_4K_picture.mp4" ;;
  deliver)
    THREADS=${THREADS:-0} /home/user/rohillavinaykrishan/tools/vfx/bin/deliver_4k.sh "$R/vinay30_4K_picture.mp4" "$WAV" "$OUT" ;;
  posters)
    for f in 374 749; do
      ffmpeg -v error -y -i "$R/vinay30_4K_picture.mp4" -vf "select=eq(n\,$f)" -vsync 0 -frames:v 1 "$R/poster_f${f}_4K.png"
    done ;;
  *) echo "usage: $0 build|proxy|half a|b|join|deliver|posters"; exit 1 ;;
esac
