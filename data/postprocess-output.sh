#!/bin/bash

ifile=~/pism/output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/y0099000-extra.nc
ofile=alps-wcnn-1km-21ka.nc

# make directory or update modification date
mkdir -p processed
touch processed
cd processed

# extract topographies time slice
ncks -O -v thk,topg,usurf -d time,4 $ifile $ofile

# add thickness mask
ncap2 -A -s "mask=byte(thk>1)" $ofile

# edit its attributes
ncatted -a pism_intent,mask,d,, \
        -a valid_min,mask,d,, \
        -a long_name,mask,o,c,"land ice binary mask" \
        -a standard_name,mask,o,c,"land_ice_binary_mask" \
        -a units,mask,o,c,"1" \
        $ofile

# remove ice thickness and permute dimensions
ncpdq -O -x -v thk -a y,x $ofile $ofile
