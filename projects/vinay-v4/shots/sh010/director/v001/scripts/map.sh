#!/bin/bash
# map.sh workdir tag extra-args...
cd /home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001
W=$1; TAG=$2; shift 2; O=$W/sparse_$TAG; rm -rf $O; mkdir -p $O; S=$(date +%s)
colmap mapper --database_path $W/database.db --image_path $W/images --output_path $O --Mapper.init_min_tri_angle 0.5 --Mapper.filter_min_tri_angle 0.3 --Mapper.local_ba_min_tri_angle 1 --Mapper.tri_min_angle 0.3 --Mapper.init_min_num_inliers 30 --Mapper.abs_pose_min_num_inliers 15 --Mapper.ba_refine_principal_point 0 --Mapper.num_threads 2 --Mapper.multiple_models 0 --Mapper.max_focal_length_ratio 100 --Mapper.min_focal_length_ratio 0.05 --Mapper.max_extra_param 100 "$@" > $W/map_$TAG.log 2>&1
R=$(for m in $O/*/; do colmap model_analyzer --path $m 2>&1 | grep -E "Registered|Points:|Mean reprojection" | sed 's/.*\] //' | tr '\n' ' '; colmap model_converter --input_path $m --output_path $m --output_type TXT >/dev/null 2>&1; grep -v "^#" $m/cameras.txt | tr '\n' ' '; done)
echo "$W $TAG t=$(( $(date +%s)-S ))s | $(ls $W/images|wc -l) imgs | $R"
