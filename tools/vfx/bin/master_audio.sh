#!/bin/bash
# Sound department: master the final mix for streaming (two-pass EBU R128 loudnorm).
#
#   master_audio.sh in.wav out.wav [youtube|spotify|instagram]
#   youtube/spotify: -14 LUFS, -1 dBTP;  instagram: -13 LUFS, -1 dBTP
set -euo pipefail
in="${1:-}"; out="${2:-}"; target="${3:-youtube}"
[ -n "$in" ] && [ -n "$out" ] || { sed -n '2,6p' "$0"; exit 2; }
case "$target" in youtube|spotify) I=-14 ;; instagram) I=-13 ;; *) sed -n '2,6p' "$0"; exit 2 ;; esac

stats=$(ffmpeg -hide_banner -nostats -i "$in" -af "loudnorm=I=$I:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$stats" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -y -loglevel error -i "$in" -af "loudnorm=I=$I:TP=-1:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true,aresample=48000" -c:a pcm_s24le "$out"
after=$(ffmpeg -hide_banner -nostats -i "$out" -af ebur128=peak=true -f null - 2>&1 | grep -E '^\s+(I|Peak):' | tr -s ' ' | tr '\n' ' ')
echo "wrote $out ($after)"
