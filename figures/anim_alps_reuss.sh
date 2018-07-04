#!/bin/bash

# animation name
name=$(basename "${0%.sh}")${1+_$1}

# prepare jumpers
for f in $name anim_alps_{sources,reality,license}${1+_$1}
do
    [ -f $f.png ] || inkscape --export-dpi=254 --export-png=$f.png $f.svg
done

# assemble video
ffmpeg -loop 1 -t 10 -i $name.png \
       -pattern_type glob -i "$HOME/anim/$name/??????.png" \
       -loop 1 -t 10 -i anim_alps_sources${1+_$1}.png \
       -loop 1 -t 05 -i anim_alps_reality${1+_$1}.png \
       -loop 1 -t 05 -i anim_alps_license${1+_$1}.png \
       -filter_complex \
           "[0:v]fade=t=in:st=0:d=1,fade=t=out:st=009:d=1[v0]; \
            [1:v]fade=t=in:st=0:d=1,fade=t=out:st=119:d=1[v1]; \
            [2:v]fade=t=in:st=0:d=1,fade=t=out:st=009:d=1[v2]; \
            [3:v]fade=t=in:st=0:d=1,fade=t=out:st=004:d=1[v3]; \
            [4:v]fade=t=in:st=0:d=1,fade=t=out:st=004:d=1[v4]; \
            [v0][v1][v2][v3][v4]concat=n=5:v=1:a=0,format=yuv420p[v]" \
       -map "[v]" -c:v libx264 -r 25 $name.mp4 -y
