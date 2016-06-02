#!/bin/bash

frames="/scratch_net/ogive/juliens/anim/anim_alps_3d_v01/%04d.png"
options="-i $frames -r 25 -pix_fmt yuv420p"

avconv $options -c:v libx264 anim_alps_3d.mp4 -y
avconv $options -c:v theora anim_alps_3d.ogg -y
