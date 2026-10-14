#!/bin/bash
# Color department: quick looks, LUTs, slow-motion and final delivery with ffmpeg.
#
#   grade.sh look   in.mp4 out.mp4 <teal-orange|warm|cool|bw|vintage|punchy|filmic>
#   grade.sh lut    in.mp4 out.mp4 my_look.cube
#   grade.sh slowmo in.mp4 out.mp4 2        # 2x slower, motion-interpolated frames
#   grade.sh deliver in.mp4 out.mp4 [uhd|uhd-vertical|youtube|reels|master]   (default: uhd = 4K)
set -euo pipefail

cmd="${1:-}"; in="${2:-}"; out="${3:-}"; arg="${4:-}"
[ -n "$cmd" ] && [ -n "$in" ] && [ -n "$out" ] || { sed -n '2,8p' "$0"; exit 2; }
enc=(-c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -c:a copy)

case "$cmd" in
  look)
    case "$arg" in
      teal-orange) vf="colorbalance=rs=-0.08:bs=0.12:rh=0.10:bh=-0.10,eq=contrast=1.08:saturation=1.15" ;;
      warm)        vf="colortemperature=temperature=4800,eq=saturation=1.08" ;;
      cool)        vf="colortemperature=temperature=8000,eq=contrast=1.05" ;;
      bw)          vf="hue=s=0,eq=contrast=1.2" ;;
      vintage)     vf="curves=preset=vintage,noise=alls=8:allf=t" ;;
      punchy)      vf="eq=contrast=1.15:saturation=1.3,unsharp=5:5:0.6" ;;
      filmic)      vf="curves=master='0/0.04 0.25/0.22 0.75/0.80 1/0.96',eq=saturation=0.92,noise=alls=4:allf=t" ;;
      *) echo "looks: teal-orange warm cool bw vintage punchy filmic"; exit 2 ;;
    esac
    ffmpeg -y -loglevel error -i "$in" -vf "$vf" "${enc[@]}" "$out" ;;
  lut)
    ffmpeg -y -loglevel error -i "$in" -vf "lut3d=file='$arg'" "${enc[@]}" "$out" ;;
  slowmo)
    factor="${arg:-2}"
    fps=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$in")
    ffmpeg -y -loglevel error -i "$in" -an \
      -vf "minterpolate=fps=($fps)*$factor:mi_mode=mci:mc_mode=aobmc:vsbmc=1,setpts=$factor*PTS,fps=$fps" \
      -c:v libx264 -crf 17 -pix_fmt yuv420p "$out" ;;
  deliver)
    case "${arg:-uhd}" in
      uhd|uhd-vertical)
        [ "$arg" = "uhd-vertical" ] && size="2160:3840" || size="3840:2160"
        ffmpeg -y -loglevel error -i "$in" \
          -vf "scale=$size:force_original_aspect_ratio=increase:flags=lanczos,crop=$size,unsharp=5:5:0.35,format=yuv420p" \
          -c:v libx264 -crf 16 -preset slow -profile:v high -level 5.1 -movflags +faststart -c:a aac -b:a 320k "$out" ;;
      youtube) ffmpeg -y -loglevel error -i "$in" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 320k "$out" ;;
      reels)   ffmpeg -y -loglevel error -i "$in" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
                 -c:v libx264 -crf 19 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 256k "$out" ;;
      master)  ffmpeg -y -loglevel error -i "$in" -c:v prores_ks -profile:v 3 -c:a pcm_s24le "$out" ;;
      *) echo "targets: uhd uhd-vertical youtube reels master"; exit 2 ;;
    esac ;;
  *) sed -n '2,8p' "$0"; exit 2 ;;
esac
echo "wrote $out"
