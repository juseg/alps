#!/bin/bash
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Render Alps 4k animations main layer.

# command-line arguments
region="${1:-alpsfix}"  # alpsfix lucerne durance zoomout
visual="${2:-velsurf}"  # bedrock erosion streams velsurf
lang="${3:-en}"  # de en fr ja it nl

# input-output prefix and frames glob pattern
prefix="$HOME/anim/alpcyc_4k"
frames="??????.png"

# time overlay
case $region in
    alpsfix | zoomout )
        time_dir="timebar_${visual}"
        time_box="c=#ffffff@0.5:s=3840x400"
        time_pos="0:H-h" ;;
    lucerne | durance )
        time_dir="timetag"
        time_box="c=#ffffff@0.5:s=560x120"
        time_pos="0:0" ;;
esac

# color bar overlay stream
case $visual in
    bedrock | erosion )
        cbar_args="-i ${prefix}_${visual}_colorbar_${lang}.png"
        cbar_filt="[geog][3]overlay[geog];"
esac

# prepare still frames
python stills.py alpcyc_4k_${visual}_${lang}.yaml --height=2160 \
    $([ $visual == streams ] && echo --subtitle $region)

# prepare filtergraph for main scene
filt="[0][1]overlay[geog];"                 # assemble geographic layer
filt+="color=${time_box}[cbox];"            # create time info color box
filt+="[cbox][2]overlay=shortest=1[time];"  # assemble time info layer
filt+="$cbar_filt"                          # overlay color bar if given
filt+="[geog][time]overlay=${time_pos}"     # overlay time info on maps
filt+=",tpad=25:25:clone:clone"             # clone first and last frames

# add title frame and bumpers
filt+=",fade=in:0:$fade,fade=out:$((secs*25-fade)):$fade[main];"  # main scene
filt+="[3]fade=in:0:$fade,fade=out:$((4*25-fade)):$fade[head];"  # title frame
filt+="[4]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[refs];"  # references
filt+="[5]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[disc];"  # disclaimer
filt+="[6]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[bysa];"  # license
filt+="[head][main][refs][disc][bysa]concat=5" \

# assemble video
ffmpeg \
    -pattern_type glob -i "${prefix}_${region}_${visual}/${frames}" \
    -pattern_type glob -i "${prefix}_${region}_citymap_${lang}/${frames}" \
    -pattern_type glob -i "${prefix}_${time_dir}_${lang}/${frames}" \
    -loop 1 -t 4 -i alpcyc_4k_${visual}_${lang}_head.png \
    -loop 1 -t 3 -i alpcyc_4k_${visual}_${lang}_refs.png \
    -loop 1 -t 3 -i alpcyc_4k_${visual}_${lang}_disc.png \
    -loop 1 -t 3 -i alpcyc_4k_${visual}_${lang}_bysa.png \
    ${cbar_args} -filter_complex "$filt" -pix_fmt yuv420p -c:v libx264 -r 25 \
    ${prefix}_${region}_${visual}_${lang}.mp4

# accelerate for social media
ffmpeg \
    -i ${prefix}_${region}_${visual}_${lang}.mp4 \
    -s 1920x1080 -vf "trim=5:125,setpts=PTS/10" \
    ${prefix}_${region}_${visual}_${lang}_x10.mp4
