#!/usr/bin/env bash
# Editor B plates: C00, B01-B08 -> plates/<ID>.mp4 (2400x900, 25 fps, ungraded, x264 crf10 yuv444p)
# usage: build_B.sh [ID ...]   (default: all). Needs edl_B.json (python3 plan_B.py edl_B.json).
set -euo pipefail
V=/home/user/rohillavinaykrishan/projects/sukanya-v2/shots/sh010/edit/v001
SRC=/home/user/rohillavinaykrishan/projects/sukanya-v2/source/trailer.mp4
S=${SCRATCH:-/tmp/claude-0/-home-user-rohillavinaykrishan/5fe3b9fd-8381-5a1b-b6a0-30ea036f781a/scratchpad}/editB
mkdir -p "$S" "$V/plates"
# active picture, 4-row top pad puts the coded 8x8 grid (crop y=92 = 8*11+4) back on block boundaries
PREP="crop=1280:536:0:92,pad=1280:540:0:4,deblock=filter=strong:block=8,crop=1280:536:0:4"
ENC=(-c:v libx264 -preset slow -crf 10 -pix_fmt yuv444p -r 25 -an -movflags +faststart)
ycrop() { python3 -c "import json;d=json.load(open('$V/edl_B.json'));print({p['id']:p.get('band_y',52) for p in d['plates']}['$1'])"; }
post() { echo "scale=2400:1005:flags=lanczos,crop=2400:900:0:$(ycrop $1),unsharp=5:5:0.4,setsar=1,format=yuv444p"; }
IDS=("$@"); [ ${#IDS[@]} -eq 0 ] && IDS=(C00 B01 B02 B03 B04 B05 B06 B07 B08)

need_mi=0; for i in "${IDS[@]}"; do [[ $i == C00 || $i == B01 ]] && need_mi=1; done
if [ $need_mi = 1 ] && [ ! -f "$S/mi/done" ]; then
  # optical-flow slow-mo source: trailer frames 3446..3454 (inside sf126 only), 24 sub-steps per frame
  rm -rf "$S/mi"; mkdir -p "$S/mi"
  SUB=$(python3 -c "
import json;d=json.load(open('$V/edl_B.json'))
ps=sorted({round((x-3446)*24) for p in d['plates'] if p['mode']=='minterpolate' for x in p['src_pos']})
print('+'.join('eq(n,%d)'%k for k in ps))")
  ffmpeg -v error -y -i "$SRC" -an -vf "select='between(n\,3446\,3454)',$PREP,settb=1,setpts=N,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,select='$SUB'" \
    -vsync 0 -frame_pts 1 "$S/mi/s_%04d.png"
  # -frame_pts names files by pts in 1/24 units = sub-step index from 3446
  touch "$S/mi/done"
fi

for ID in "${IDS[@]}"; do
  MODE=$(python3 -c "import json;d=json.load(open('$V/edl_B.json'));print([p['mode'] for p in d['plates'] if p['id']=='$ID'][0])")
  if [ "$MODE" = minterpolate ]; then
    python3 - "$V/edl_B.json" "$ID" "$S" > "$S/$ID.txt" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); p=[x for x in d['plates'] if x['id']==sys.argv[2]][0]
for x in p['src_pos']:
    print("file '%s/mi/s_%04d.png'\nduration 0.04" % (sys.argv[3], round((x-3446)*24)))
PY
    ffmpeg -v error -y -f concat -safe 0 -i "$S/$ID.txt" -vf "settb=1/25,setpts=N,$(post $ID)" -frames:v $(python3 -c "import json;d=json.load(open('$V/edl_B.json'));print([p['frames'] for p in d['plates'] if p['id']=='$ID'][0])") "${ENC[@]}" "$V/plates/$ID.mp4"
  else
    SEL=$(python3 -c "import json;d=json.load(open('$V/edl_B.json'));p=[p for p in d['plates'] if p['id']=='$ID'][0];print('+'.join('eq(n,%d)'%k for k in p['src_pos']))")
    ffmpeg -v error -y -i "$SRC" -an -vf "select='$SEL',$PREP,settb=1/25,setpts=N,$(post $ID)" "${ENC[@]}" "$V/plates/$ID.mp4"
  fi
  echo "$ID: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames,width,height,r_frame_rate -of csv=p=0 "$V/plates/$ID.mp4")"
done
