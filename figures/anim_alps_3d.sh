#!/bin/bash

framedir="/scratch_net/ogive/juliens/anim/anim_alps_3d_v01/"

ffmpeg -i $framedir/%04d.png -c:v libx264 -pix_fmt yuv420p anim_alps_3d.mp4 -y
