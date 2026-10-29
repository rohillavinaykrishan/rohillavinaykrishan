#!/bin/bash
# Beekeeper 2 re-cut: edit + correction + hero grade. Usage: build.sh <W> <out.mp4> [upscaled_picture.mp4]  (W=1920 or 3840)
# With an AI-upscaled picture (3840x1608, already cropped, from shots/final/upscale) the crop/denoise steps are skipped.
set -e
P=/home/user/rohillavinaykrishan/projects/beekeeper2_trailer
SRC=$P/source/trailer_original.mp4; W=$1; OUT=$2; UP=$3
if [ -n "$UP" ]; then PIC="[1:v]setpts=PTS-STARTPTS"; DN=""; SIG=30; else PIC="[0:v]crop=1280:536:0:92,setpts=PTS-STARTPTS"; DN="hqdn3d=2:1.5:3:3,"; SIG=10; fi
H=$((W*9/16)); PH=$((W*536/1280/2*2)); PY=$(((H-PH)/2))
# grade at source res (1280x536 picture), times are source seconds
CORR="${DN}format=gbrp,\
eq=gamma=1.35:enable='between(t,23.98,24.94)+between(t,40.54,41.71)+between(t,64.23,65.07)+between(t,65.52,66.02)',\
colorbalance=rs=0.05:bs=-0.06:rm=0.05:bm=-0.06:enable='between(t,43.88,47.59)',\
colorbalance=gs=-0.06:gm=-0.06:rm=0.02:enable='between(t,26.98,30.49)+between(t,59.10,60.39)+between(t,62.19,62.73)',\
colorbalance=gm=-0.04:rm=0.02:enable='between(t,69.90,71.74)'"
LOOK="curves=master='0/0.015 0.22/0.17 0.5/0.5 0.78/0.83 1/0.97',\
colorbalance=rs=-0.07:gs=0.01:bs=0.07:rh=0.07:gh=0.03:bh=-0.07,\
colorbalance=bm=0.03:rm=-0.02:enable='lt(t,37.43)',\
colorbalance=rm=0.04:gm=0.01:bm=-0.04:enable='gte(t,47.6)',\
eq=saturation=1.08:contrast=1.04"
GLOW="format=gbrp,split[g0][g1];[g1]curves=master='0/0 0.7/0 1/0.8',gblur=sigma=$SIG[gl];[g0][gl]blend=all_mode=screen:all_opacity=0.28"
ffmpeg -y -v error -stats -i $SRC ${UP:+-i $UP} -filter_complex "\
$PIC[v];[v]split=3[a][b][c];\
[a]trim=0.5:54.304,setpts=PTS-STARTPTS[A];\
[b]trim=54.304:55.264,setpts=PTS-STARTPTS,tmix=frames=5,eq=brightness=-0.12:contrast=0.9[B];\
[c]trim=55.264:75.38,setpts=PTS-STARTPTS[C];\
[A][B][C]concat=n=3:v=1:a=0,settb=1/24000,setpts=PTS+0.5/TB,\
$CORR,$LOOK,$GLOW,\
eq=brightness=0.35:enable='between(t,30.19,30.24)+between(t,37.43,37.47)+between(t,47.67,47.71)',\
scale=$W:$PH:flags=lanczos,format=yuv420p,noise=alls=5:allf=t,vignette=angle=0.35,\
pad=$W:$H:0:$PY:black,fps=24,setpts=PTS-0.5/TB,fade=t=out:st=74.2:d=0.68,format=yuv420p[vo];\
[0:a]atrim=0.5:75.38,asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[ao]" \
-map "[vo]" -map "[ao]" -c:v libx264 -preset medium -crf 19 -maxrate $((W/1920*16))M -bufsize $((W/1920*32))M -profile:v high -tag:v avc1 -c:a aac -b:a 320k -movflags +faststart -t 74.88 $OUT
