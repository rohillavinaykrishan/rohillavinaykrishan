#!/bin/bash
D=/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/lighting/v002
cd $D; rm -f $D/borders.jsonl
$D/scripts/waitslot.sh
echo "start $(date +%T)"
blender -b -P scripts/shot_scene.py -- $D 2808 16 0-51 $D/sh010_lighting_v002.blend 2>&1 | grep -E "BORDER|FRAME|rror|Traceback|Saved.*blend" | grep -v -E "CUEW|EGL"
/opt/vfx-ai/bin/python scripts/fix_shadow.py $D
echo "end $(date +%T)"
