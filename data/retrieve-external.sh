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
if [ ! -f srtm.nc ]
then

    # download ETOPO1 data
    eroot="https://ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/"
    eroot+="cell_registered/georeferenced_tiff"
    efile="ETOPO1_Bed_c_geotiff"
    wget -nc $eroot/$efile.zip
    unzip -n $efile.zip

    # download SRTM data
    sroot="https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF"
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

    # patch modern glacier thickness
    root="/run/media/julien/archive/orig/geodata/glaciers/thickness/original"
    gdalbuildvrt thk32.vrt -a_srs EPSG:32632 -srcnodata 0 \
        $root/europe-utm32/thick/thick_?????.agr
    gdalbuildvrt thk33.vrt -a_srs EPSG:32633 -srcnodata 0 \
        $root/europe-utm33/thick/thick_?????.agr
    gdalwarp -t_srs EPSG:32632 -te 100000 4820000 1100000 5420000 -tr 100 100 \
             -r cubic -ot Int16 thk{32,33}.vrt thk.tif

    # combine topo and thickness
    gdal_translate -of netcdf srtm.{tif,nc} && ncrename -v z,usurf srtm.nc
    gdal_translate -of netcdf thk.{tif,nc} && ncrename -v Band1,thk thk.nc
    ncks -A -v thk thk.nc srtm.nc
    nccopy -sd1 srtm.nc thk.nc && mv thk.nc srtm.nc

    # remove intermediate tiffs
    rm thk.tif srtm.tif

fi

# Swisstopo Vector 500
if [ ! -f 22_DKM500_GEWAESSER_PLY.shp ] || [ ! -f 25_DKM500_GEWAESSER_LIN.shp ]
then
    wget -nc https://data.geo.admin.ch/ch.swisstopo.swiss-map-vector500.metadata/SMV500_SHAPE_CHLV95.zip
    unzip -jn SMV500_SHAPE_CHLV95.zip \
        "20161001_SMV500_SHAPE_CHL95/Shapefiles/22_DKM500_GEWAESSER_PLY.???" \
        "20161001_SMV500_SHAPE_CHL95/Shapefiles/25_DKM500_GEWAESSER_LIN.???"
    rm SMV500_SHAPE_CHL95.zip
fi

# Swisstopo Geology 500
if [ ! -f PY_Surface_Base.shp ]
then
    wget -nc https://data.geo.admin.ch/ch.swisstopo.geologie-geologische_karte/data.zip
    unzip -jn data.zip GK500_V1_3_Vector.zip
    unzip -jn GK500_V1_3_Vector.zip \
        "GK500_V1_3_FR/Shapes/PY_Surface_Base.???"
    rm data.zip GK500_V1_3_Vector.zip
fi

# Spratt et al. (2016) sea level curve
wget -nc https://www1.ncdc.noaa.gov/pub/data/paleo/contributions_by_author/\
spratt2016/spratt2016.txt
