#!/bin/bash
# solve.sh : full COLMAP solve of the 52 plate frames at 1280x536 (treatment 9.2)
L=/home/user/rohillavinaykrishan/projects/vinay-v4/shots/sh010/layout/v001; W=$L/colmap; S=$(date +%s)
rm -rf $W/database.db $W/sparse; mkdir -p $W/sparse
colmap feature_extractor --database_path $W/database.db --image_path $W/images --ImageReader.single_camera 1 --ImageReader.camera_model SIMPLE_RADIAL --SiftExtraction.use_gpu 0 --SiftExtraction.max_num_features 8000 --SiftExtraction.num_threads 2 > $W/log.txt 2>&1
echo "features done $(( $(date +%s)-S ))s" >> $W/time.txt
colmap exhaustive_matcher --database_path $W/database.db --SiftMatching.use_gpu 0 --SiftMatching.num_threads 2 >> $W/log.txt 2>&1
echo "match done $(( $(date +%s)-S ))s" >> $W/time.txt
colmap mapper --database_path $W/database.db --image_path $W/images --output_path $W/sparse --Mapper.init_min_tri_angle 0.5 --Mapper.filter_min_tri_angle 0.3 --Mapper.local_ba_min_tri_angle 1 --Mapper.tri_min_angle 0.3 --Mapper.init_min_num_inliers 30 --Mapper.abs_pose_min_num_inliers 15 --Mapper.ba_refine_principal_point 0 --Mapper.num_threads 2 --Mapper.multiple_models 0 --Mapper.max_focal_length_ratio 100 --Mapper.min_focal_length_ratio 0.05 --Mapper.max_extra_param 100 > $W/mapper.log 2>&1
echo "mapper done $(( $(date +%s)-S ))s" >> $W/time.txt
for m in $W/sparse/*/; do colmap model_analyzer --path $m 2>&1 | sed 's/.*\] //' ; colmap model_converter --input_path $m --output_path $m --output_type TXT; grep -v "^#" $m/cameras.txt; done > $W/analyzer.txt 2>&1
echo "ALL DONE $(( $(date +%s)-S ))s" >> $W/time.txt
