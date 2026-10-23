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
# Tested 2026-10-23 (light test, no full render): a 1 s stream-copy cut (27 frames) of
#   projects/sukanya-v2/deliver/Sukanya_Dilip_Dhariya_StreetFighter_SrMatchmove_v2_4K.mp4 (delivered file untouched,
#   md5 49c6ec79...) + projects/sukanya-v2/shots/sh010/sound/v001/master.wav:
#   ffmpeg -i <delivered>.mp4 -t 1 -an -c copy cut1s.mp4
#   THREADS=2 deliver_4k.sh cut1s.mp4 .../sound/v001/master.wav <scratchpad>/d4k/test_4K.mp4
# RESULT: exit 0, 37 s wall for 27 frames at THREADS=2 (~1.4 s/frame -> ~15-18 min for a 750-frame 30 s master).
#   h264 High L5.2 yuv420p bt709/bt709/bt709 2160x3840 25/1 r+avg, 27 frames (all input frames kept), start 0.000;
#   aac LC 48000 Hz 2 ch 327 kb/s, start 0.000, 1.066 s vs video 1.080 s (-shortest, < 1 frame); 183 Mb/s.
#   ebur128 on this 1 s cut: I -14.9 LUFS, Peak -5.5 (on a 1 s cut these are not meaningful; judge on the full master).
set -euo pipefail
usage() { sed -n '2,29p' "$0"; exit 2; }
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
