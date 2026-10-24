#!/bin/bash
# cm3.sh name start dur  -> ~<=36 frames, 960x402, exhaustive, low-angle mapper
cd /home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/director/v001
N=$1; W=cm4_$N; rm -rf $W; mkdir -p $W/images $W/sparse; S=$(date +%s)
FPS=$(python3 -c "print(min(23.976, 36/$3))")
ffmpeg -hide_banner -loglevel error -y -ss $2 -t $3 -i ../../../../source/trailer.mp4 -vf "fps=$FPS,crop=1280:536:0:92,scale=640:268" -q:v 1 $W/images/%04d.jpg
colmap feature_extractor --database_path $W/database.db --image_path $W/images --ImageReader.single_camera 1 --ImageReader.camera_model SIMPLE_RADIAL --SiftExtraction.use_gpu 0 --SiftExtraction.max_num_features 6000 --SiftExtraction.num_threads 2 > $W/log.txt 2>&1
colmap exhaustive_matcher --database_path $W/database.db --SiftMatching.use_gpu 0 --SiftMatching.num_threads 2 >> $W/log.txt 2>&1
colmap mapper --database_path $W/database.db --image_path $W/images --output_path $W/sparse --Mapper.init_min_tri_angle 0.5 --Mapper.filter_min_tri_angle 0.3 --Mapper.local_ba_min_tri_angle 1 --Mapper.tri_min_angle 0.3 --Mapper.init_min_num_inliers 30 --Mapper.abs_pose_min_num_inliers 15 --Mapper.ba_refine_principal_point 0 --Mapper.num_threads 2 --Mapper.multiple_models 0 --Mapper.max_focal_length_ratio 100 --Mapper.min_focal_length_ratio 0.05 --Mapper.max_extra_param 100 >> $W/log.txt 2>&1
R=$(for m in $W/sparse/*/; do colmap model_analyzer --path $m 2>&1 | grep -E "Registered|Points:|Mean reprojection" | sed 's/.*\] //' | tr '\n' ' '; done)
G=$(python3 -c "
import sqlite3;c=sqlite3.connect('$W/database.db');print(dict(c.execute('select config,count(*) from two_view_geometries group by config').fetchall()))")
echo "$N $2+$3 frames=$(ls $W/images|wc -l) t=$(( $(date +%s)-S ))s | $R | cfg $G"
