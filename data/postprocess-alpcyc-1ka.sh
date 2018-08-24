#!/bin/bash

# Prepare ALPCYC 1ka snapshots and scalar timeseries.
#
# I find NCO syntax a bit clumsy, and preserving history far from intuitive.
# It may actually be easier to use python and xarray.

# make directory or update modification date
mkdir -p processed
touch processed
cd processed

# extra variables to mask and to include
mvars="tempicethk_basal temppabase thk $(echo {u,v}vel{base,surf})"
evars="pism_config topg $mvars"  # variables not to mask

# selected runs properties
gridres=(2km 2km 2km 2km 2km 2km 1km)
records=(grip grip epica epica md012444 md012444 epica)
pparams=(cp pp cp pp cp pp pp)
offsets=(0820 1040 0970 1220 0800 1060 1220)

# loop on selected runs
for i in {0..6}
do
    res="${gridres[$i]}"
    rec="${records[$i]}"
    pp="${pparams[$i]}"
    dt="${offsets[$i]}"

    # config string and time stride (happens to be the same for extra and ts)
    [ "$res" == "1km" ] && stride="99,,100" || stride="9,,10"
    [ "$pp" == "pp" ] && conf="alpcyc4+pp" || conf="alpcyc4"

    # input and output file locations
    bfile="$HOME/pism/input/boot/alps-srtm+thk+gou11simi-$res.nc"
    efile="$HOME/pism/output/e9d2d1f/alps-wcnn-$res/${rec}3222cool$dt+$conf"
    blink="alpcyc.$res.boot.nc"                 # link to boot file
    elink="alpcyc.$res.${rec:0:4}.$pp.extra"    # link to extra file
    ofile="alpcyc.$res.${rec:0:4}.$pp.1ka.nc"   # snapshots output file
    sfile="alpcyc.$res.${rec:0:4}.$pp.sts.nc"   # timeseries output file
    tfile="alpcyc.$res.${rec:0:4}.$pp.tmp.nc"   # multipurpose tmp file

    # message
    echo "preparing $ofile..."

    # link output files (newer nco forbids + in file names)
    # FIXME: remove all + in pism folders on all computers
    ln -fs $efile $elink
    ln -fs $bfile $blink

    # concatenate output files and copy history from last file
    ncrcat -O -d time,$stride -v ${evars// /,} $elink/*-extra.nc $ofile
    ncks -A -h -x $elink/y0120000-extra.nc $ofile
    ncrcat -O -d time,$stride -v ${evars// /,} $elink/*-ts.nc $sfile
    ncks -A -h -x $elink/y0120000-ts.nc $sfile

    # apply mask and add fill value
    ncap2 -A -s "where(thk<1.0){$(for v in $mvars; do echo -n "$v=-2e9;"; done)};\
    $(for v in $mvars; do echo -n "$v.set_miss(-2e9);"; done)" $ofile

    # extract boot topography, rename it, edit its attributes and append
    ncks -O -v topg $blink $tfile
    ncpdq -O -a y,x $tfile $tfile
    ncrename -v topg,boot_topg $tfile
    ncatted -h -a coordinates,boot_topg,o,c,"lat lon" \
               -a grid_mapping,boot_topg,o,c,"mapping" \
               -a long_name,boot_topg,o,c,"initial bedrock surface elevation" \
               -a standard_name,boot_topg,o,c,"initial_bedrock_altitude" $tfile
    ncks -A -v boot_topg $tfile $ofile

    # add titles
    prefix="Alpine ice sheet glacial cycle simulations"
    ncatted -h -a title,global,o,c,"$prefix millennial snapshots" $ofile
    ncatted -h -a title,global,o,c,"$prefix scalar time series" $sfile

    # remove (mostly) duplicate history and add global attributes
    inst="ETH Zürich, Switzerland and Hokkaido University, Japan"

    for f in $ofile $sfile
    do
        ncatted -h -a history_of_appended_files,global,d,, $ofile
        ncatted -h -a author,global,o,c,"Julien Seguinot" $ofile
        ncatted -h -a institution,global,o,c,"$inst" $ofile
    done

    # compress with shuffling and remove links
    nccopy -sd1 $ofile $tfile && mv $tfile $ofile
    nccopy -sd1 $sfile $tfile && mv $tfile $sfile
    rm $blink $elink

done
