#!/bin/bash

# make directory or update modification date
mkdir -p processed
touch processed
cd processed

# Post-process 1km extra dataset
# ------------------------------

# pism output file
idir="$HOME/pism/input"
odir="$HOME/pism/output/e9d2d1f"
bestrun="alps-wcnn-1km/epica3222cool1220+alpcyc4+pp"
bfile="$idir/boot/alps-srtm+thk+gou11simi-1km.nc"
efile="$odir/$bestrun/y0099000-extra.nc"
ofile="${bestrun/"/"/-}-21000a.nc"
vars=thk,topg,usurf

# extract boot topography
echo "preparing $ofile ..."
ncks -O -v topg $bfile $ofile

# rename it and edit its attributes
ncrename -O -v topg,boot_topg $ofile $ofile
ncatted -a coordinates,boot_topg,o,c,"lat lon" \
        -a grid_mapping,boot_topg,o,c,"mapping" \
        -a long_name,boot_topg,o,c,"initial bedrock surface elevation" \
        -a standard_name,boot_topg,o,c,"initial_bedrock_altitude" \
        $ofile

# permute dimensions
ncpdq -O -a y,x $ofile $ofile

# append 21ka time slice
ncks -A -v $vars -d time,-1 $efile $ofile

# compute thickness mask
ncap2 -A -s "mask=byte(thk>1)" $ofile
ncatted -a pism_intent,mask,d,, \
        -a valid_min,mask,d,, \
        -a long_name,mask,o,c,"land ice binary mask" \
        -a standard_name,mask,o,c,"land_ice_binary_mask" \
        -a units,mask,o,c,"1" \
        $ofile

# compute bedrock uplift
ncap2 -A -s "uplift=float(topg-boot_topg)" $ofile
ncatted -a pism_intent,uplift,d,, \
        -a long_name,uplift,o,c,"bedrock uplift relative to initial topography" \
        -a standard_name,uplift,o,c,"bedrock_altitude_change_due_to_isostatic_adjustment" \
        $ofile
