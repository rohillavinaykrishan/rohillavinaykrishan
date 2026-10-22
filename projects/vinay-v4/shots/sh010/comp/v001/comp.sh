#!/usr/bin/env bash
# sh010 comp v001: rebuilds every output from upstream files.
#   usage: bash comp.sh [all|prep|comp|encode]
# Upstream: color/v002/plate_graded, lighting/v002/{cg,shadow,mist}, layout/v001/distort.py, roto/v001/matte.
# Frame numbering 0000-0051 = s0-s51 everywhere; output movies are 25 fps (1:1 frame conform, f169-220).
set -euo pipefail
V=/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/comp/v001
SH=/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010
W=$V/work
STEP=${1:-all}
UP="scale=2808:1176:flags=lanczos+accurate_rnd+full_chroma_int,format=gbrp,cas=strength=0.55"
PRORES="-c:v prores_ks -profile:v 4 -pix_fmt yuv444p10le -vendor apl0 -color_primaries bt709 -color_trc bt709 -colorspace bt709"
H264="-c:v libx264 -preset slow -tune film -crf 16 -pix_fmt yuv420p -profile:v high -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart"

if [[ $STEP == all || $STEP == prep ]]; then
  mkdir -p $W/plate_up $W/grain
  # 1. plate: lanczos 2.19x + contrast-adaptive sharpen 0.55 (no unsharp haloes)
  ffmpeg -v error -y -start_number 0 -i $SH/color/v002/plate_graded/plate.%04d.png \
    -vf "$UP,format=rgb48le" -start_number 0 $W/plate_up/plate.%04d.png
  # 2. CG passes: solved SIMPLE_RADIAL lens, 1.16 overscan -> 2808x1176
  for p in cg shadow mist; do
    vfx-python $SH/layout/v001/distort.py "$SH/lighting/v002/$p/$p.%04d.png" "$W/${p}_d/$p.%04d.png" \
      --width 2808 --overscan 1.16 --frames 0-51
  done
  # 3. matched grain: the colorist's luma grain (noise c0s=5:c0f=t, finish_filter_v002) on 50% grey, same upscale
  ffmpeg -v error -y -f lavfi -i "color=c=0x808080:s=1280x536:r=25,format=yuv444p" -frames:v 52 \
    -vf "noise=c0s=5:c0f=t,format=rgb24,$UP,format=gray16le" -start_number 0 $W/grain/grain.%04d.png
fi

if [[ $STEP == all || $STEP == comp ]]; then
  # 4. per-frame comp (see scripts/comp.py header for the chain and parameters)
  vfx-python $V/scripts/comp.py --frames 0-51 | tee $W/comp.log
fi

if [[ $STEP == all || $STEP == encode ]]; then
  mkdir -p $V/final_2808 $V/final_2160 $V/plate_2160 $V/cg_2160
  cp $W/final/final.*.png $V/final_2808/
  DOWN="scale=2160:904:flags=lanczos+accurate_rnd+full_chroma_int"
  ffmpeg -v error -y -start_number 0 -i $W/final/final.%04d.png -vf "$DOWN" -start_number 0 $V/final_2160/final.%04d.png
  ffmpeg -v error -y -start_number 0 -i $W/cgband/cg.%04d.png -vf "$DOWN" -start_number 0 $V/cg_2160/cg.%04d.png
  ffmpeg -v error -y -start_number 0 -i $SH/color/v002/plate_graded/plate.%04d.png \
    -vf "scale=2160:904:flags=lanczos+accurate_rnd+full_chroma_int,format=gbrp,cas=strength=0.55,format=rgb24" \
    -start_number 0 $V/plate_2160/plate.%04d.png
  enc() {  # seq name
    ffmpeg -v error -y -framerate 25 -start_number 0 -i "$1" $PRORES $V/$2.mov
    ffmpeg -v error -y -framerate 25 -start_number 0 -i "$1" $H264 $V/$2.mp4
  }
  enc "$V/final_2808/final.%04d.png" final_band_2808x1176
  enc "$V/final_2160/final.%04d.png" final_band_2160x904
  enc "$V/plate_2160/plate.%04d.png" plate_band_2160x904
  enc "$V/cg_2160/cg.%04d.png"       cg_band_2160x904
fi
echo "comp.sh $STEP done"
