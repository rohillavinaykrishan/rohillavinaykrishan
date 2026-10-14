#!/bin/bash
# Post-effect looks for any image or video (renders, footage, comps) with ffmpeg.
#
#   post_look.sh <look> in.mp4 out.mp4      (also works on .png/.jpg)
#
# Looks: glow, dream, pixel, scanlines, rgbsplit, vhs, film, comic, mirror, kaleido
set -euo pipefail

look="${1:-}"; in="${2:-}"; out="${3:-}"
[ -n "$look" ] && [ -n "$in" ] && [ -n "$out" ] || { sed -n '2,7p' "$0"; exit 2; }

scan="drawgrid=w=iw:h=4:t=1:c=black@0.35"
case "$look" in
  glow)      fc="format=gbrp,split[a][b];[b]gblur=sigma=18[g];[a][g]blend=all_mode=screen:all_opacity=0.65" ;;
  dream)     fc="format=gbrp,split[a][b];[b]gblur=sigma=40,eq=brightness=0.05[g];[a][g]blend=all_mode=screen:all_opacity=0.8,eq=saturation=0.85" ;;
  pixel)     fc="scale=iw/10:ih/10:flags=neighbor,scale=iw*10:ih*10:flags=neighbor" ;;
  scanlines) fc="$scan" ;;
  rgbsplit)  fc="rgbashift=rh=-8:bh=8:gv=2" ;;
  vhs)       fc="rgbashift=rh=-4:bh=4,gblur=sigma=0.8,noise=alls=14:allf=t,eq=saturation=1.35:contrast=1.1,$scan" ;;
  film)      fc="curves=master='0/0.05 0.5/0.48 1/0.95',noise=alls=7:allf=t,vignette=PI/4.5" ;;
  comic)     fc="format=gbrp,split[a][b];[b]edgedetect=low=0.1:high=0.3,negate[e];[a]eq=saturation=1.6,lutrgb=r='floor(val/48)*48':g='floor(val/48)*48':b='floor(val/48)*48'[c];[c][e]blend=all_mode=multiply" ;;
  mirror)    fc="crop=iw/2:ih:0:0,split[l][r];[r]hflip[rf];[l][rf]hstack" ;;
  kaleido)   fc="crop=iw/2:ih/2:0:0,split[a][b];[b]hflip[bf];[a][bf]hstack,split[c][d];[d]vflip[df];[c][df]vstack" ;;
  *) sed -n '2,7p' "$0"; exit 2 ;;
esac

case "${in,,}" in
  *.png|*.jpg|*.jpeg|*.tif|*.tiff|*.exr)
    ffmpeg -y -loglevel error -i "$in" -filter_complex "$fc" -frames:v 1 "$out" ;;
  *)
    ffmpeg -y -loglevel error -i "$in" -filter_complex "[0:v]$fc,format=yuv420p" \
      -c:v libx264 -crf 17 -preset medium -c:a copy "$out" ;;
esac
echo "wrote $out"
