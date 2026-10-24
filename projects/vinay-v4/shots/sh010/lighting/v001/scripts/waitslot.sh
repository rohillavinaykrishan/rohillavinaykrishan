#!/bin/bash
# wait until fewer than 2 heavy jobs run (ignores shells)
while true; do
 n=$(ps -eo args | grep -E "^(colmap|blender|/usr/local/bin/blender|[^ ]*python[^ ]* [^ ]*(sam_roto|roto\.py)|.*hyperframes render)" | grep -v -E "^/bin/bash|grep" | wc -l)
 [ "$n" -lt 2 ] && break
 sleep 10
done
