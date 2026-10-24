#!/usr/bin/env bash
# graded plate delivery + which source each MG is using
cd /home/user/rohillavinaykrishan/projects/vinay-30s/shots/sh010
TZ=Asia/Kolkata date +%H:%M:%S
echo "color plates: $(ls color/v001/plates/*.mp4 2>/dev/null | wc -l)/40  notes=$( [ -f color/v001/notes.md ] && echo y || echo n)"
echo "mg1 inputs: $(grep -o '"kind": "[a-z]*"' mograph/v001/mg1/inputs.json | sort | uniq -c | tr -s ' ' | tr '\n' ' ')"
echo "mg2 H0 -> $(readlink mograph/v001/mg2/assets/H0.mp4)"
echo "mg3 inputs: $(grep -o ': [a-z]*"' mograph/v001/mg3/build_inputs.json | sort | uniq -c | tr -s ' ' | tr '\n' ' ')"
