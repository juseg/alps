#!/bin/bash

# make directory or update modification date
mkdir -p processed
touch processed
cd processed

# Post-process 1km extra dataset
# ------------------------------

# pism output file
odir=$HOME/pism/output/0.7.3
runname=alps-wcnn-1km/epica3222cool0950+acyc1+esia5
ifile=$odir/$runname/extra.nc
ofile=${runname/"/"/-}-21ka.nc
vars=thk,topg,usurf

# extract 21ka time slice
echo "preparing $ofile ..."
ncks -O -v $vars -d time,989 $ifile $ofile

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
