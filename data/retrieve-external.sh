#!/bin/bash

# make directory or update modification date
mkdir -p external
touch external
cd external

## Ehlers et al. (2011) LGM outline
#if [ ! -f lgm_alpen.shp.tif ]
#then
#   root="http://static.us.elsevierhealth.com/ehlers_digital_maps"
#   arch="digital_maps_02_all_other_files.zip"
#   wget -nc $root/$name
#   unzip -jn $name lgm_alpen.???
#fi

# SRTM surface topographic data
if [ ! -f srtm.tif ]
then

    # download ETOPO1 data
    eroot="https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/"\
         "cell_registered/georeferenced_tiff"
    efile="ETOPO1_Bed_c_geotiff"
    wget -nc $eroot/$efile
    unzip -n $efile

    # download SRTM data
    sroot="https://srtm.csi.cgiar.org/SRT-ZIP/SRTM_V41/SRTM_Data_GeoTiff"
    for sfile in srtm_{37..41}_{03..04}
    do
        wget -nc $sroot/$sfile.zip
        unzip -n $sfile.zip $sfile.{hdr,tfw,tif}
    done

    # patch and reproject for the Alps
    # -te 150000 4820000 1050000 5420000 #  900x600 km domain
    # -te 112500 4855000 1087500 5355000 #  950x500 km poster
    # -te 100000 4820000 1100000 5420000 # 1000x600 km both
    gdalwarp -r cubic -s_srs EPSG:4326 -t_srs EPSG:32632 \
             -te 100000 4820000 1100000 5420000 -tr 100 100 \
             $efile.tif srtm_??_??.tif srtm.tif

fi

# Modern glacier thickness
if [ ! -f thk.tif ]
then
    root="/run/media/julien/archive/orig/geodata/glaciers/thickness/original"
    gdalbuildvrt thk32.vrt -a_srs EPSG:32632 -srcnodata 0 \
        $root/europe-utm32/thick/thick_?????.agr
    gdalbuildvrt thk33.vrt -a_srs EPSG:32633 -srcnodata 0 \
        $root/europe-utm33/thick/thick_?????.agr
    gdalwarp -t_srs EPSG:32632 -te 100000 4820000 1100000 5420000 -tr 100 100 \
             -r cubic -ot Int16 thk{32,33}.vrt thk.tif
fi

# Swisstopo Vector 500
if [ ! -f 22_DKM500_GEWAESSER_PLY.shp ] || [ ! -f 25_DKM500_GEWAESSER_LIN.shp ]
then
    wget $orig
    unzip -jn data.zip 20161001_SMV500_SHAPE_CHL95.zip
    unzip -jn 20161001_SMV500_SHAPE_CHL95.zip \
        "20161001_SMV500_SHAPE_CHL95/Shapefiles/22_DKM500_GEWAESSER_PLY.???" \
        "20161001_SMV500_SHAPE_CHL95/Shapefiles/25_DKM500_GEWAESSER_LIN.???"
    rm data.zip 20161001_SMV500_SHAPE_CHL95.zip
fi

# Swisstopo Geology 500
if [ ! -f PY_Surface_Base.shp ]
then
    wget https://data.geo.admin.ch/ch.swisstopo.geologie-geologische_karte/data.zip
    unzip -jn data.zip GK500_V1_3_Vector.zip
    unzip -jn GK500_V1_3_Vector.zip \
        "GK500_V1_3_FR/Shapes/PY_Surface_Base.???"
    rm data.zip GK500_V1_3_Vector.zip
fi
