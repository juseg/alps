#!/bin/bash

name="anim_alps_cycle"
frames="/scratch_net/iceberg/juliens/anim/$name/%04d00.png"
options="-i $frames -r 25 -pix_fmt yuv420p"

avconv $options -c:v libx264 $name.mp4 -y
avconv $options -c:v theora $name.ogg -y
