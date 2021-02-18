#!/bin/bash

# animation name
name=$(basename "${0%.sh}")
orig="$HOME/anim/$name"  # folder containing animation frames
dest="$name.tms"  # destination folder for tiles

# find gdal2tiles command
gdal2tiles="$(command -v gdal2tiles.py || command -v gdal2tiles2.py)"

# loop on frames
for year in {001..120..1}000
do

    # locally link current frame
    ln -sf $orig/$year.png $name.png

    # prepare tiles
    [ -d $dest/$year ] || $gdal2tiles -r antialias -s "EPSG:32632" \
        -w none -z 6-10 $name.png $dest/$year

done
