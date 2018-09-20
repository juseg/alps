#!/bin/bash

# parse command-line arguments
crop="${1:-al}"  # al ch
over="${2:-ttag}"  # ttag tbar
lang="${3:-en}"  # de en fr

# prepare bumpers
for f in anim_alps_bp_{4k_${crop/zo/al},refs,disc,bysa}_$lang
do
    inkscape --export-dpi=508 --export-png=$f.png $f.svg
done

# color box and overlay position
case $over in
    'tbar') box="c=#ffffff@0.5:s=3840x400"; pos="0:H-h" ;;
    'ttag') box="c=#ffffff@0.5:s=480x120"; pos="0:0" ;;
    *) echo "invalid overlay $over, exiting." ;;
esac

# assembling parametres
imgs="??????.png"  # images to include, edit for quick tests
fade=12  # number of frames for fade in and fade out effects
hold=25  # number of frames to hold in the beginning and end
secs=$((120+2*hold/25))  # duration of main scene in seconds

# prepare filtergraph for main scene
filt=""
filt+="color=${box}[c];"                # create time info color box
filt+="nullsrc=s=3840x2160:d=$secs[n];" # create fixed duration stream
filt+="[0][1]overlay[geog];"            # assemble geographic layer
filt+="[c][2]overlay=shortest=1[info];" # assemble time info layer
filt+="[geog][info]overlay=${pos}"      # overlay time info on maps
filt+=",loop=$hold:1:0,[n]overlay"      # hold first and last frames

# add title frame and bumpers
filt+=",fade=in:0:$fade,fade=out:$((secs*25-fade)):$fade[main];"  # main scene
filt+="[3]fade=in:0:$fade,fade=out:$((4*25-fade)):$fade[head];"  # title frame
filt+="[4]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[refs];"  # references
filt+="[5]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[disc];"  # disclaimer
filt+="[6]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[bysa];"  # license
filt+="[head][main][refs][disc][bysa]concat=5" \

# assemble video
ffmpeg \
    -pattern_type glob -i "$HOME/anim/anim_alps_4k_main_${crop}/$imgs" \
    -pattern_type glob -i "$HOME/anim/anim_alps_4k_city_${crop}_$lang/$imgs" \
    -pattern_type glob -i "$HOME/anim/anim_alps_4k_${over}_$lang/$imgs" \
    -loop 1 -t 4 -i anim_alps_bp_4k_${crop/zo/al}_$lang.png \
    -loop 1 -t 3 -i anim_alps_bp_refs_$lang.png \
    -loop 1 -t 3 -i anim_alps_bp_disc_$lang.png \
    -loop 1 -t 3 -i anim_alps_bp_bysa_$lang.png \
    -filter_complex $filt -pix_fmt yuv420p -c:v libx264 -r 25 \
    $HOME/anim/anim_alps_4k_${crop}_${over}_${lang}.mp4
