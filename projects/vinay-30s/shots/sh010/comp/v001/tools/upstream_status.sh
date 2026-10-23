#!/usr/bin/env bash
# prints one line per MG: scene html files, proxies, notes (signals that a part has landed)
cd /home/user/rohillavinaykrishan/projects/vinay-30s/shots/sh010/mograph/v001
TZ=Asia/Kolkata date +%H:%M:%S
for m in mg1 mg2 mg3; do
  echo "$m: html=[$(cd $m 2>/dev/null && ls compositions/*.html index.html 2>/dev/null | tr '\n' ' ')] proxy=[$(ls $m/*proxy* $m/*/*proxy* 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')] notes=$( [ -f $m/notes.md ] && echo y || echo n)"
done
