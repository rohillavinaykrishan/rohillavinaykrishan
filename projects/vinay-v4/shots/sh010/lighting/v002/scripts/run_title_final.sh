#!/bin/bash
D=/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/lighting/v002
cd $D
for m in bg fg; do
  $D/scripts/waitslot.sh
  echo "start $m $(date +%T)"
  blender -b -t 4 -P scripts/title_scene.py -- $m $D/title_$m.png 2160 64 $D/title_$m.blend 2>&1 | grep -E "rror|RENDER_SEC|Traceback|DIMS|Saved" | grep -v CUEW
  echo "end $m $(date +%T)"
done
