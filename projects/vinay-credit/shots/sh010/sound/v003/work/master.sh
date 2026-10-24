#!/bin/bash
# pre-limit (numpy look-ahead TP limiter, -5.2 dBTP) -> master_audio.sh youtube (loudnorm, verified linear) -> static trim to -14.00 LUFS BS.1770
set -euo pipefail; cd "$(dirname "$0")/.."; M=/home/user/rohillavinaykrishan/tools/vfx/bin/master_audio.sh; C=-5.2; : > work/limiter_log.txt
for pair in "mix_raw.wav:mix_master.wav" "mix_noaccents_raw.wav:mix_master_no_accents.wav"; do in=${pair%%:*}; out=${pair##*:}
 vfx-python work/peak_limit.py $in work/pre_$in $C >> work/limiter_log.txt
 st=$(ffmpeg -hide_banner -nostats -i work/pre_$in -af "loudnorm=I=-14:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p'); get(){ echo "$st" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
 echo "$in loudnorm pass2: $(ffmpeg -hide_banner -nostats -i work/pre_$in -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true:print_format=json" -f null - 2>&1 | grep normalization_type | tr -d '\t')"
 $M work/pre_$in work/ln_$out youtube
 tr=$(vfx-python work/lufs.py work/ln_$out | sed 's/.*I=\([-0-9.]*\).*/\1/'); trim=$(python3 -c "print(round(-14.0-($tr),3))"); echo "static trim $trim dB"
 ffmpeg -y -v error -i work/ln_$out -af "volume=${trim}dB" -c:a pcm_s24le -ar 48000 $out
done
grep -E "max GR|10.1-10.6|12.28" work/limiter_log.txt | cut -c1-60
vfx-python work/lufs.py mix_master.wav mix_master_no_accents.wav
for f in mix_master.wav mix_master_no_accents.wav; do echo "$f ebur128: $(ffmpeg -hide_banner -nostats -i $f -af ebur128=peak=true -f null - 2>&1 | grep -E '^\s+(I|LRA|Peak):' | tr -s ' ' | tr '\n' ' ')"; done
