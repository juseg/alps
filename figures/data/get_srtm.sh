#!/bin/bash

url="http://srtm.csi.cgiar.org/SRT-ZIP/SRTM_V41/SRTM_Data_GeoTiff/srtm_38_02.zip"
archive="/scratch_net/ogive/juliens/geodata/topography/cgiar/srtm_38_03.zip"
input=${archive%.zip}.tif
output=srtm.nc

# download archive
[ -f $archive ] || wget $url

# inflate archive
[ -f $input ] || unzip $archive

# reproject to UTM 32
gdalwarp -s_srs EPSG:4326 -t_srs EPSG:32632 \
         -te 0 4500000 1500000 5500000 -tr 250 250 \
         -wm 512 -wo SOURCE_EXTRA=1000 \
         -srcnodata -32768 -dstnodata -32768 \
         -of netcdf -overwrite \
         $input $output

