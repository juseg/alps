#!/bin/bash
# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Alps scatter plot animation script
# ----------------------------------

# assembling parametres
imgs="??????.png"  # images to include, edit for quick tests
fade=12  # number of frames for fade in and fade out effects
hold=25  # number of frames to hold in the beginning and end
secs=$((120+2*hold/25))  # duration of main scene in seconds

# prepare filtergraph for main scene
filt+="nullsrc=s=1920x1080:d=$secs[n];" # create fixed duration stream
filt+="[0]loop=$hold:1:0,[n]overlay"    # hold first and last frames

## add title frame and bumpers
#filt+=",fade=in:0:$fade,fade=out:$((secs*25-fade)):$fade[main];"  # main scene
#filt+="[3]fade=in:0:$fade,fade=out:$((4*25-fade)):$fade[head];"  # title frame
#filt+="[4]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[refs];"  # references
#filt+="[5]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[disc];"  # disclaimer
#filt+="[6]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[bysa];"  # license
#filt+="[head][main][refs][disc][bysa]concat=5" \

# assemble video  # FIXME bumbers
ffmpeg \
    -pattern_type glob -i "$HOME/anim/anim_alps_dots/$imgs" \
    -filter_complex $filt -pix_fmt yuv420p -c:v libx264 -r 25 \
    $HOME/anim/anim_alps_dots.mp4
    #-loop 1 -t 4 -i anim_alps_4k_al_er_en_head.png \
    #-loop 1 -t 3 -i anim_alps_4k_al_er_en_refs.png \
    #-loop 1 -t 3 -i anim_alps_4k_al_er_en_disc.png \
    #-loop 1 -t 3 -i anim_alps_4k_al_er_en_bysa.png \
