#!/bin/bash
# sheet.sh out.png post_filter lut1 [lut2 ...]  -> row0 = before, one row per LUT (LUT + post filter)
set -e
D=${FRAMES:-/home/user/rohillavinaykrishan/projects/vinay-credit/shots/sh010/color/v001/frames}
OUT=$1; POST=$2; shift 2
T=$(mktemp -d)
rows=()
ffmpeg -v error -y $(for s in A B C D E F G H I J; do echo -i $D/$s.png; done) -filter_complex "hstack=inputs=10" $T/r0.png; rows+=($T/r0.png)
i=1
for L in "$@"; do
  for s in A B C D E F G H I J; do ffmpeg -v error -y -i $D/$s.png -vf "format=rgb24,lut3d=file=$L${POST:+,$POST}" $T/$i$s.png; done
  ffmpeg -v error -y $(for s in A B C D E F G H I J; do echo -i $T/$i$s.png; done) -filter_complex "hstack=inputs=10" $T/r$i.png; rows+=($T/r$i.png); i=$((i+1))
done
ffmpeg -v error -y $(for r in "${rows[@]}"; do echo -i $r; done) -filter_complex "vstack=inputs=${#rows[@]},scale=iw/2:-1" $OUT 2>/dev/null || ffmpeg -v error -y -i ${rows[0]} -vf scale=iw/2:-1 $OUT
rm -rf $T
