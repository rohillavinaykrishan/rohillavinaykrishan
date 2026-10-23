#!/usr/bin/env bash
# Delivery: mux a finished picture + the mastered audio into the 4K client master (settings from the
# shipped sukanya-v2 comp.sh "4k" step).
#
#   deliver_4k.sh <video_no_audio_or_with.mp4> <audio.wav> <out_4K.mp4>
#
#   video : any picture (its own audio, if any, is ignored). Size is NOT changed: render/scale to
#           2160x3840 (or 3840x2160) first. Frame rate is forced to 25 (-r 25).
#   audio : the master WAV (sound dept, already -14 LUFS / <= -1 dBTP; AAC adds ~0.1-0.3 dB of peak).
#   out   : refuses to overwrite an existing file (delete or version it yourself; never touch deliver/ copies
#           that were already sent).
#   env   : THREADS=N (x264 threads, default 0 = auto; use 2 when other heavy jobs run).
#
#   Encode: libx264 -preset slow -crf 12 -tune film -profile:v high -level 5.2 -pix_fmt yuv420p -r 25 -g 50,
#           BT.709 primaries/trc/matrix, tv range; AAC 320k -cutoff 20000 48 kHz; -shortest; +faststart.
#   Then prints the ffprobe summary and the ebur128 (I, LRA, true peak) of the result.
#   Follow with: vfx-python tools/vfx/bin/auto_qc.py <out> --expect-frames N --out review/qc.md
#
#   Heavy job (4K x264 slow ~ 1-2 s/frame on this box): check pgrep first, at most 2 heavy jobs.
#
# Tested 2026-10-23 (light test, 1 s only, no full render): 25-frame 4K stream-copy cut of
#   projects/sukanya-v2/deliver/Sukanya_..._v2_4K.mp4 + projects/sukanya-v2/shots/sh010/sound/v001/master.wav
#   THREADS=2 deliver_4k.sh cut1s.mp4 master.wav <scratch>/test_4K.mp4
#   -> RESULT: see the line below (filled from the real run).
# RESULT: h264 High L5.2 yuv420p bt709 2160x3840 25/1, 25 frames, 1.000 s; aac LC 48000 Hz 2 ch 320k,
#   start 0/0; ebur128 on 1 s = no gated integrated value (I needs >400 ms of signal above gate; use the
#   full master); encode 31 s wall at THREADS=2 (~1.2 s/frame -> ~15 min for a 30 s / 750-frame master).
set -euo pipefail
usage() { sed -n '2,27p' "$0"; exit 2; }
[ $# -eq 3 ] || usage
in="$1"; wav="$2"; out="$3"
[ -f "$in" ] || { echo "no video: $in"; exit 2; }
[ -f "$wav" ] || { echo "no audio: $wav"; exit 2; }
[ -e "$out" ] && { echo "refusing to overwrite $out"; exit 2; }
for f in "$in" "$wav"; do [ "$(realpath "$f")" = "$(realpath -m "$out")" ] && { echo "out = input"; exit 2; }; done
mkdir -p "$(dirname "$out")"

t0=$(date +%s)
ffmpeg -hide_banner -v error -stats -y -i "$in" -i "$wav" -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset slow -crf 12 -tune film -profile:v high -level 5.2 -pix_fmt yuv420p -r 25 -g 50 \
  -threads "${THREADS:-0}" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 320k -cutoff 20000 -ar 48000 \
  -shortest -movflags +faststart "$out"
echo "encoded in $(( $(date +%s) - t0 )) s -> $out"

echo "--- ffprobe"
ffprobe -v error -count_packets -show_entries \
  stream=codec_name,profile,level,pix_fmt,color_space,color_transfer,color_primaries,width,height,r_frame_rate,avg_frame_rate,nb_read_packets,start_time,duration,sample_rate,channels,bit_rate \
  -of compact=p=0 "$out"
ffprobe -v error -show_entries format=duration,size,bit_rate -of compact=p=0 "$out"
echo "--- ebur128 (target -14 LUFS +/- 0.5, <= -1 dBTP)"
ffmpeg -hide_banner -nostats -i "$out" -vn -af ebur128=peak=true -f null - 2>&1 \
  | sed -n '/Summary:/,$p' | grep -E '^\s+(I|LRA|Peak):' | tr -s ' '
