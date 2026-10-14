#!/bin/bash
# Color department: quick looks, LUTs, slow-motion and final delivery with ffmpeg.
#
#   grade.sh look   in.mp4 out.mp4 <look>   (movie: cinematic, blockbuster, moody, bleach, noir;
#                                            song: bollywood, romantic, golden-hour, night-neon, dreamy;
#                                            basic: teal-orange, warm, cool, bw, vintage, punchy, filmic)
#   grade.sh lut    in.mp4 out.mp4 my_look.cube
#   grade.sh slowmo in.mp4 out.mp4 2        # 2x slower, motion-interpolated frames
#   grade.sh deliver in.mp4 out.mp4 [uhd|uhd-vertical|youtube|reels|master]   (default: uhd = 4K)
#   grade.sh split  in.mp4 out_dir [seconds]   # parts that rejoin frame-exactly + full_audio.wav
set -euo pipefail

cmd="${1:-}"; in="${2:-}"; out="${3:-}"; arg="${4:-}"
[ -n "$cmd" ] && [ -n "$in" ] && [ -n "$out" ] || { sed -n '2,11p' "$0"; exit 2; }
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
      cinematic)   vf="colorbalance=rs=-0.06:gs=-0.02:bs=0.10:rh=0.08:gh=0.02:bh=-0.08,curves=master='0/0.03 0.25/0.20 0.75/0.82 1/0.97',eq=saturation=0.9,vignette=PI/5" ;;
      blockbuster) vf="colorbalance=rs=-0.12:bs=0.16:rm=0.04:bm=-0.04:rh=0.12:bh=-0.12,curves=master='0/0 0.2/0.14 0.8/0.88 1/1',eq=saturation=1.1:contrast=1.06,unsharp=5:5:0.4" ;;
      moody)       vf="colorbalance=bs=0.10:gs=0.03:bm=0.04,curves=master='0/0.02 0.3/0.2 0.7/0.62 1/0.9',eq=saturation=0.72,vignette=PI/4" ;;
      bleach)      vf="split[a][b];[b]hue=s=0[g];[a][g]blend=all_mode=overlay:all_opacity=1,eq=contrast=1.18:saturation=0.45" ;;
      noir)        vf="hue=s=0,curves=master='0/0 0.3/0.18 0.7/0.82 1/1',eq=contrast=1.25,vignette=PI/3.5,noise=alls=6:allf=t" ;;
      bollywood)   vf="colortemperature=temperature=5200,colorbalance=rm=0.05:gm=-0.01:rh=0.06,eq=saturation=1.35:contrast=1.08:brightness=0.02,unsharp=5:5:0.3" ;;
      romantic)    vf="colortemperature=temperature=5000,curves=master='0/0.08 0.5/0.55 1/0.96',colorbalance=rh=0.05:bh=0.03,eq=saturation=0.85,gblur=sigma=0.6" ;;
      golden-hour) vf="colortemperature=temperature=4200,colorbalance=rh=0.10:gh=0.04:bs=0.04,curves=master='0/0.03 0.5/0.53 1/0.97',eq=saturation=1.15" ;;
      night-neon)  vf="colorbalance=rs=0.06:bs=0.16:rh=0.10:bh=0.06:gm=-0.06,curves=master='0/0 0.25/0.12 0.75/0.85 1/1',eq=saturation=1.22:contrast=1.1" ;;
      dreamy)      vf="split[a][b];[b]gblur=sigma=25[g];[a][g]blend=all_mode=screen:all_opacity=0.3,curves=master='0/0.03 1/0.98',eq=saturation=0.95" ;;
      *) echo "looks: cinematic blockbuster moody bleach noir bollywood romantic golden-hour night-neon dreamy teal-orange warm cool bw vintage punchy filmic"; exit 2 ;;
    esac
    case "${in,,}" in
      *.png|*.jpg|*.jpeg|*.tif|*.tiff) ffmpeg -y -loglevel error -i "$in" -filter_complex "format=gbrp,$vf" -frames:v 1 "$out" ;;
      *) ffmpeg -y -loglevel error -i "$in" -filter_complex "[0:v]format=gbrp,$vf,format=yuv420p" "${enc[@]}" "$out" ;;
    esac ;;
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
  split)
    secs="${arg:-60}"
    mkdir -p "$out"
    ffmpeg -y -loglevel error -i "$in" -map 0:v -map 0:a? \
      -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -force_key_frames "expr:gte(t,n_forced*$secs)" \
      -c:a aac -b:a 320k -f segment -segment_time "$secs" -reset_timestamps 1 "$out/part_%02d.mp4"
    if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$in" | grep -q .; then
      ffmpeg -y -loglevel error -i "$in" -map 0:a -c:a pcm_s16le "$out/full_audio.wav"
    fi
    ls "$out" ;;
  *) sed -n '2,11p' "$0"; exit 2 ;;
esac
echo "wrote $out"
