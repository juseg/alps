#!/bin/bash
# Copyright (c) 2016-2022, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# make directory or update modification date
mkdir -p external
touch external
cd external

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
