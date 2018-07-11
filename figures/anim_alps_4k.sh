#!/bin/bash -ex

# parse command-line arguments
crop="${1:-al}"  # al ch
over="${2:-ttag}"  # ttag tbar
lang="${3:-en}"  # de en fr

# prepare bumpers
for f in anim_alps_bp_{4k_${crop},refs,disc,bysa}_$lang
do
    [ -f $f.png ] || inkscape --export-dpi=508 --export-png=$f.png $f.svg
done

# color box and overlay position
case $over in
    'tbar') box="c=#ffffff@0.5:s=3840x400"; pos="0:H-h" ;;
    'ttag') box="c=#ffffff@0.5:s=480x120"; pos="0:0" ;;
    *) echo "invalid overlay $over, exiting." ;;
esac

# prepare filtergraph for main scene
filt=""
filt+="color=${box}[c];"                # create time info color box
filt+="nullsrc=s=3840x2160:d=124[n];"   # create fixed duration stream
filt+="[0][1]overlay[geog];"            # assemble geographic layer
filt+="[c][2]overlay=shortest=1[info];" # assemble time info layer
filt+="[geog][info]overlay=${pos}"      # overlay time info on maps
filt+=",loop=50:1:0,[n]overlay"         # hold first and last frames

# add title frame and bumpers
filt+=",fade=in:st=0:d=1,fade=out:st=123:d=1[main];"  # main scene
filt+="[3]fade=in:st=0:d=1,fade=out:st=7:d=1[head];"  # title frame
filt+="[4]fade=in:st=0:d=1,fade=out:st=5:d=1[refs];"  # references
filt+="[5]fade=in:st=0:d=1,fade=out:st=5:d=1[disc];"  # disclaimer
filt+="[6]fade=in:st=0:d=1,fade=out:st=5:d=1[bysa];"  # license
filt+="[head][main][refs][disc][bysa]concat=5" \

# assemble video
ffmpeg \
    -pattern_type glob -i "$HOME/anim/anim_alps_4k_main_${crop}/??????.png" \
                       -i "$HOME/anim/anim_alps_4k_city_${crop}/$lang.png" \
    -pattern_type glob -i "$HOME/anim/anim_alps_4k_${over}_$lang/??????.png" \
    -loop 1 -t 8 -i anim_alps_bp_4k_${crop}_$lang.png \
    -loop 1 -t 6 -i anim_alps_bp_refs_$lang.png \
    -loop 1 -t 6 -i anim_alps_bp_disc_$lang.png \
    -loop 1 -t 6 -i anim_alps_bp_bysa_$lang.png \
    -filter_complex $filt -pix_fmt yuv420p -c:v libx264 -r 25 \
    anim_alps_4k_${crop}_${over}_${lang}.mp4
