#!/bin/bash
echo "Set FFM_FILE and FFM_TARGET_WIDTH"
ffmpeg -i $FFM_FILE -vf scale=$FFM_TARGET_WIDTH:-1 -r 15 frames/out%04d.png
