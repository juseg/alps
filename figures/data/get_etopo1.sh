#!/bin/bash

url="http://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/\
grid_registered/georeferenced_tiff/ETOPO1_Bed_c_geotiff.zip"
archive="/scratch_net/ogive/juliens/geodata/topography/etopo1/\
ETOPO1_Bed_c_geotiff.zip"
input=${archive%.zip}.tif
output=etopo1.nc

# download archive
[ -f $archive ] || wget $url

# inflate archive
[ -f $input ] || unzip $archive

# reproject to UTM 32
gdalwarp -s_srs EPSG:4326 -t_srs EPSG:32632 \
         -te 0 4500000 1500000 5500000 -tr 1000 1000 \
         -wm 512 -wo SOURCE_EXTRA=1000 \
         -srcnodata -32768 -dstnodata -32768 \
         -of netcdf -overwrite \
         $input $output
