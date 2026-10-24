#!/bin/bash
# Sound v001 master: linear gain + true-peak-safe limiter (4x oversampled look-ahead alimiter), back to 48 kHz/24-bit.
# usage: master.sh in.wav out.wav GAIN_DB [LIMIT_DBFS=-2.0]
set -euo pipefail
in=$1; out=$2; g=$3; lim=${4:--2.0}
ll=$(python3 -c "print(10**($lim/20))")
ffmpeg -y -loglevel error -i "$in" -af "volume=${g}dB,aresample=192000:resampler=soxr:precision=28,alimiter=limit=${ll}:attack=2:release=60:level=disabled:asc=1:latency=1,aresample=48000:resampler=soxr:precision=28" -c:a pcm_s24le "$out"
ffmpeg -hide_banner -nostats -i "$out" -af ebur128=peak=true -f null - 2>&1 | grep -E '^\s+(I|LRA|Peak):' | tr -s ' ' | tr '\n' ' '; echo
