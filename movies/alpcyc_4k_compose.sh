#!/bin/bash
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Compose overlays for selected frame only

# parameters
prefix="$HOME/anim/alpcyc_4k"
region="alpsfix"
visual="streams"
years="095440"
lang="en"

# city frame depends on region
[ $region == "alpsfix" ] && cframe="120000" || cframe="$years"

# compose overlays
mkdir -p ${prefix}_${region}_${visual}_composite_${lang}
magick convert -gravity south \
    ${prefix}_${region}_${visual}/${years}.png \
    ${prefix}_${region}_citymap_${lang}/${cframe}.png -composite \
    -fill '#ffffff80' -draw 'rectangle 0,1760,3840,2160' \
    ${prefix}_timebar_${visual}_${lang}/${years}.png -composite \
    ${prefix}_${region}_${visual}_composite_${lang}/${years}.png
