#!/bin/bash
# sheet.sh in.mp4 out.png  -> 7x2 contact sheet of the EDL check frames, frame numbers burned in
IN=$1; OUT=$2
F="0 25 72 96 120 143 168 193 231 255 299 307 340 374"
SEL=$(for f in $F; do printf "eq(n\\\\,%d)+" $f; done); SEL=${SEL%+}
ffmpeg -y -v error -i "$IN" -vf "scale=270:480,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='%{eif\:n\:d}':x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6,select='$SEL',tile=7x2:padding=4" -frames:v 1 -fps_mode passthrough "$OUT"
