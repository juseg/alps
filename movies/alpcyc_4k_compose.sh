#!/bin/bash
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Compose overlays for selected frame only

# parameters
prefix="$HOME/anim/alpcyc_4k"
region="zoomout"
years="035000"

# city frame depends on region
[ $region == "alpsfix" ] && cframe="120000" || cframe="$years"

# compose overlays
mkdir -p ${prefix}_${region}_streams_composite_de
magick convert -gravity south \
    ${prefix}_${region}_streams/${years}.png \
    ${prefix}_${region}_citymap_de/${cframe}.png -composite \
    -fill '#ffffff80' -draw 'rectangle 0,1760,3840,2160' \
    ${prefix}_timebar_streams_de/${years}.png -composite \
    ${prefix}_${region}_streams_composite_de/${years}.png
