#!/bin/bash
# Design department: render an HTML/CSS design to a PNG with headless Chromium
# (thumbnails, title cards, storyboards, social graphics).
#
#   html2png.sh design.html out.png [WIDTHxHEIGHT]      default 1280x720 (YouTube thumbnail)
# The page should be exactly WIDTHxHEIGHT (html,body{width:..;height:..}). Local images can be
# referenced with relative paths. Fonts available: Inter, DejaVu, plus any Google Font via <link>.
set -euo pipefail
in="${1:-}"; out="${2:-}"; size="${3:-1280x720}"
[ -n "$in" ] && [ -n "$out" ] || { sed -n '2,7p' "$0"; exit 2; }
w="${size%x*}"; h="${size#*x}"
chrome=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1)
[ -x "$chrome" ] || chrome=$(command -v chromium || command -v google-chrome)
tmp=$(mktemp --suffix=.png)
# Pin the page box to the target size so absolutely positioned elements anchor to it,
# not to Chromium's viewport (which differs from the window size in headless mode).
page="$(dirname "$(realpath "$in")")/.html2png_$$.html"
sed "0,/<head[^>]*>/s//&<style>html,body{position:relative!important;width:${w}px!important;height:${h}px!important;overflow:hidden!important;margin:0}<\/style>/" "$in" > "$page"
trap 'rm -f "$page" "$tmp"' EXIT
# render taller than needed (headless window chrome eats some height), then crop exact
"$chrome" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size="$w,$((h + 200))" --virtual-time-budget=3000 --screenshot="$tmp" "file://$page" >/dev/null 2>&1
convert "$tmp" -crop "${w}x${h}+0+0" +repage "$out"
echo "wrote $out ($(identify -format '%wx%h, %b' "$out"))"
