#!/bin/bash

# Prepare ALPCYC continuous variables
# -----------------------------------

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
    pexfile="alpcyc.$res.${rec:0:4}.$pp.ex.1ka.nc"  # processed extra file
    ptsfile="alpcyc.$res.${rec:0:4}.$pp.ts.10a.nc"  # timeseries output file
    tmpfile="alpcyc.$res.${rec:0:4}.$pp.tmp.nc"     # multipurpose tmp file

    # message
    echo "preparing $pexfile..."

    # link output files (newer nco forbids + in file names)
    # FIXME: remove all + in pism folders on all computers
    ln -fs $efile $elink
    ln -fs $bfile $blink

    # concatenate output files and copy history from last file
    ncrcat -O -d time,$stride -v ${evars// /,} $elink/*-extra.nc $pexfile
    ncks -A -h -x $elink/y0120000-extra.nc $pexfile
    ncrcat -O -d time,$stride -v ${evars// /,} $elink/*-ts.nc $ptsfile
    ncks -A -h -x $elink/y0120000-ts.nc $ptsfile

    # apply mask and add fill value
    ncap2 -A -s "where(thk<1.0){$(for v in $mvars; do echo -n "$v=-2e9;"; done)};\
    $(for v in $mvars; do echo -n "$v.set_miss(-2e9);"; done)" $pexfile

    # extract boot topography, rename it, edit its attributes and append
    ncks -O -v topg $blink $tmpfile
    ncpdq -O -a y,x $tmpfile $tmpfile
    ncrename -v topg,boot_topg $tmpfile
    ncatted -h -a coordinates,boot_topg,o,c,"lat lon" \
               -a grid_mapping,boot_topg,o,c,"mapping" \
               -a long_name,boot_topg,o,c,"initial bedrock surface elevation" \
               -a standard_name,boot_topg,o,c,"initial_bedrock_altitude" \
               $tmpfile
    ncks -A -v boot_topg $tmpfile $pexfile

    # add titles
    prefix="Alpine ice sheet glacial cycle simulations"
    ncatted -h -a title,global,o,c,"$prefix spatial diagnostics" $pexfile
    ncatted -h -a title,global,o,c,"$prefix scalar time series" $ptsfile

    # add subtitles
    [ "$pp" == "pp" ] && wo="with" || wo="without"
    subtitle="$res ${rec^^} simulation $wo precipitation reductions"
    ncatted -h -a subtitle,global,o,c,"$subtitle" $pexfile
    ncatted -h -a subtitle,global,o,c,"$subtitle" $ptsfile

    # remove (mostly) duplicate history and add global attributes
    inst="ETH Zürich, Switzerland and Hokkaido University, Japan"

    for f in $pexfile $ptsfile
    do
        ncatted -h -a history_of_appended_files,global,d,, $f
        ncatted -h -a author,global,o,c,"Julien Seguinot" $f
        ncatted -h -a institution,global,o,c,"$inst" $f
    done

    # compress with shuffling and remove links
    nccopy -sd1 $pexfile $tmpfile && mv $tmpfile $pexfile
    nccopy -sd1 $ptsfile $tmpfile && mv $tmpfile $ptsfile
    rm $blink $elink

done
