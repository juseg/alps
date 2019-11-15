#!/bin/bash

# Prepare ALPCYC input variables
# ------------------------------

# make directory or update modification date
mkdir -p processed
touch processed
cd processed

# selected runs properties
gridres=(2km 2km 2km 2km 2km 2km 1km)
records=(grip grip epica epica md012444 md012444 epica)
pparams=(cp pp cp pp cp pp pp)
offsets=(0820 1040 0970 1220 0800 1060 1220)

# copy temperature offset files
for i in {0..6}
do
    res="${gridres[$i]}"
    rec="${records[$i]}"
    pp="${pparams[$i]}"
    dt="${offsets[$i]}"

    # message
    ofile="alpcyc.$res.${rec:0:4}.$pp.dt.nc"
    echo "preparing $ofile..."

    # compress with shuffling
    nccopy -sd1 "$HOME/pism/input/dt/${rec}.3222.$dt.nc" $ofile

    # add global attributes
    [ "$pp" == "pp" ] && wo="with" || wo="without"
    title="Alpine ice sheet glacial cycle simulations input variables"
    inst="ETH Zürich, Switzerland and Hokkaido University, Japan"
    subtitle="$res ${rec^^} simulation $wo precipitation reductions"
    ncatted -h -a title,global,o,c,"$title" $ofile
    ncatted -h -a author,global,o,c,"Julien Seguinot" $ofile
    ncatted -h -a institution,global,o,c,"$inst" $ofile
    ncatted -h -a subtitle,global,o,c,"$subtitle" $ofile

done

# merge spatial input files
for res in 2km 1km
do

    # input and output file locations
    ofile="alpcyc.$res.in.nc"
    tfile="${ofile%nc}sd1.nc"

    # message
    echo "preparing $ofile..."

    # merge all input files
    cp "$HOME/pism/input/boot/alps.srtm.hus12.gou11simi.$res.nc" $ofile
    ncks -A "$HOME/pism/input/atm/alps.wcnn.$res.nc" $ofile
    ncks -A "$HOME/pism/input/sd/alps.erai.$res.nc" $ofile
    ncpdq -O -a y,x $ofile $ofile

    # remove (mostly) duplicate history and add global attributes
    title="Alpine ice sheet glacial cycle simulations input variables"
    inst="ETH Zürich, Switzerland and Hokkaido University, Japan"
    ncatted -h -a history_of_appended_files,global,d,, $ofile
    ncatted -h -a title,global,o,c,"$title" $ofile
    ncatted -h -a author,global,o,c,"Julien Seguinot" $ofile
    ncatted -h -a institution,global,o,c,"$inst" $ofile

    # compress with shuffling
    nccopy -sd1 $ofile $tfile && mv $tfile $ofile

done
