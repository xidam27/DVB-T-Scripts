#!/bin/bash

SOURCE=$1
TARGET=$2

export FFREPORT=file=/tmp/BBC_ONE_HD_ffreport.log:level=32; mkdir -p ${TARGET}; ~/bin/ffmpeg -report -nostats \
											     -t 30 \
											     -i "${SOURCE}" \
											     -stats \
											     -flush_packets 0 \
											     -threads 0 \
											     -c:v libx264  -profile:v baseline  -strict -2 -crf 8 -maxrate 2200k  -bufsize 1835k -pix_fmt yuv420p -flags -global_header -level 4.0 -preset slow -sc_threshold 0 -force_key_frames "expr:gte(t,n_forced*1)" \
											     -vf yadif -strict -2 -vf scale=iw*.5:ih*.5 \
											     -c:a libmp3lame \
											     -bsf:v h264_mp4toannexb -map 0:0 -map 0:1 \
											     -flags -global_header \
											     -f segment -segment_format mpegts \
											     -segment_list "${TARGET}/playlist.m3u8" \
											     -segment_list_type m3u8 \
											     -segment_list_flags live \
											     -bsf:v h264_mp4toannexb \
											     -segment_time 3 \
											     ${TARGET}/segment_%03d.ts -y
