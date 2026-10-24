#!/usr/bin/env bash
# sh010 comp v001 - rebuild the master from upstream files and render.
#   ./comp.sh build            sync sub-comps into master/ (tools/build_master.py) + lint
#   ./comp.sh proxy            1080x1920 draft render of the 2160 layout -> 540x960 proxy with audio
#   ./comp.sh 4k               native 2160x3840 render (ALONE: refuses if another heavy job runs) + audio mux
# The master is 2160x3840 @ 25 fps, 450 frames. Audio = sound/v001/master.wav (muxed by ffmpeg, not by HyperFrames).
set -euo pipefail
V=/home/user/rohillavinaykrishan/projects/sukanya-v2/shots/sh010/comp/v001
WAV=/home/user/rohillavinaykrishan/projects/sukanya-v2/shots/sh010/sound/v001/master.wav
R=$V/render
mkdir -p "$R"
cd "$V/master"

build() {
  python3 "$V/tools/build_master.py"
  npx hyperframes lint 2>&1 | tail -1
}

mux() {  # $1 = silent video in, $2 = out
  ffmpeg -v error -y -i "$1" -i "$WAV" -map 0:v:0 -map 1:a:0 -c:v copy \
    -c:a aac -b:a 320k -cutoff 20000 -ar 48000 -shortest -movflags +faststart "$2"
}

case "${1:-}" in
  build) build ;;
  proxy)
    build
    npx hyperframes render . --resolution portrait -q draft -f 25 -o "$R/_proxy1080.mp4" --quiet > "$R/proxy_render.log" 2>&1
    ffmpeg -v error -y -i "$R/_proxy1080.mp4" -vf scale=540:960:flags=lanczos -an -c:v libx264 -crf 18 -pix_fmt yuv420p "$R/_proxy540_v.mp4"
    mux "$R/_proxy540_v.mp4" "$R/sukanya_v2_proxy540.mp4"
    rm -f "$R/_proxy1080.mp4" "$R/_proxy540_v.mp4"
    ;;
  4k)
    if pgrep -fa "hyperframes render|chrome-headless|ffmpeg|blender|sam_roto" | grep -v -e pgrep -e comp.sh -e ccr-ca-store >/dev/null; then
      echo "another heavy job is running:"; pgrep -fa "hyperframes render|chrom|ffmpeg|blender" | cut -c1-160; exit 3
    fi
    build
    # lossless-ish intermediate from HyperFrames, then the delivery encode (crf 12, film, yuv420p) + AAC 320k
    npx hyperframes render . -q delivery --crf 8 -f 25 -o "$R/_4k_hf.mp4" > "$R/render_4k.log" 2>&1
    ffmpeg -v error -y -i "$R/_4k_hf.mp4" -i "$WAV" -map 0:v:0 -map 1:a:0 \
      -c:v libx264 -preset slow -crf 12 -tune film -pix_fmt yuv420p -profile:v high -level 5.2 -r 25 \
      -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
      -c:a aac -b:a 320k -cutoff 20000 -ar 48000 -shortest -movflags +faststart "$R/sukanya_v2_4K.mp4"
    rm -f "$R/_4k_hf.mp4"
    ;;
  *) echo "usage: $0 build|proxy|4k"; exit 1 ;;
esac
