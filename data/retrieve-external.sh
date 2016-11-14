#!/bin/bash

# make directory or update modification date
mkdir -p external
touch external
cd external

# Ehlers et al. (2011) LGM outline
#orig=http://static.us.elsevierhealth.com/ehlers_digital_maps/\
#digital_maps_02_all_other_files.zip
#dest=ehlers-etal-2011.zip
#[ -f "$dest" ] || wget $orig -O $dest
#unzip -jn $dest lgm_alpen.???

# ETOPO1 Bed original cell-registered data
orig=http://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/\
cell_registered/georeferenced_tiff/ETOPO1_Bed_c_geotiff.zip
dest=etopo1-world.tif
if [ ! -f "$dest" ]
then
    wget $orig -O ${dest%.tif}.zip
    unzip -n ${dest%.tif}.zip
    rm ${dest%.tif}.zip
fi

# ETOPO1 reprojection for the Alps
gdalwarp -s_srs EPSG:4326 -t_srs EPSG:32632 -r bilinear \
         -te 0 4500000 1500000 5500000 -tr 1000 1000 \
         -srcnodata -2147483648 -dstnodata -32768 \
         -wm 512 -wo SOURCE_EXTRA=100 -of netcdf -overwrite \
         $dest etopo1-alps.nc

# SRTM original cell-registered data
orig=http://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/\
cell_registered/georeferenced_tiff/ETOPO1_Bed_c_geotiff.zip
dest=etopo1-world.tif
orig="http://srtm.csi.cgiar.org/SRT-ZIP/SRTM_V41/SRTM_Data_GeoTiff/srtm_38_03.zip"
dest=srtm_38_03.tif
if [ ! -f "$dest" ]
then
    wget $orig -O ${dest%.tif}.zip
    unzip -n ${dest%.tif}.zip ${dest%.tif}.???
    rm ${dest%.tif}.zip
fi

# reproject to UTM 32
gdalwarp -s_srs EPSG:4326 -t_srs EPSG:32632 -r bilinear \
         -te 0 4500000 1500000 5500000 -tr 250 250 \
         -srcnodata -2147483648 -dstnodata -32768 \
         -wm 512 -wo SOURCE_EXTRA=100 -of netcdf -overwrite \
         $dest srtm-alps.nc

# Swisstopo Geology 500
orig=http://data.geo.admin.ch/ch.swisstopo.geologie-geologische_karte/data.zip
dest=swisstopo-geology.shp
if [ ! -f swisstopo-geology.shp ]
then
    wget $orig -O ${dest%.shp}.zip
    unzip -jn ${dest%.shp}.zip "Shapes/Geologie_Fl?chen.???"
    for f in Geologie_Fl?chen.???
    do
        mv $f swisstopo-geology.${f#*.}
    done
    rm ${dest%.shp}.zip
fi
