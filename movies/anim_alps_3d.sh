#!/bin/bash

name=$(basename "${0%.sh}")

ffmpeg -pattern_type glob -i "$HOME/anim/${name}_v01/????.png" -r 25 \
    -pix_fmt yuv420p -c:v libx264 $name.mp4 -y
