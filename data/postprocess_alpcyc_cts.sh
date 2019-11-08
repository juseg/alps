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

    # config string and time stride
    [ "$res" == "1km" ] && extimes="99,,100" || extimes="9,,10"
    [ "$res" == "1km" ] && tstimes="9,,10" || tstimes=",,1"
    [ "$pp" == "pp" ] && conf="alpcyc4+pp" || conf="alpcyc4"

    # input and output file locations
    efile="$HOME/pism/output/e9d2d1f/alps-wcnn-$res/${rec}3222cool$dt+$conf"
    elink="alpcyc.$res.${rec:0:4}.$pp.extra"    # link to extra file
    pexfile="alpcyc.$res.${rec:0:4}.$pp.ex.1ka.nc"  # processed extra file
    ptsfile="alpcyc.$res.${rec:0:4}.$pp.ts.10a.nc"  # timeseries output file
    tmsfile="alpcyc.$res.${rec:0:4}.$pp.tms.nc"     # timestamps output file

    # message
    echo "preparing $pexfile..."

    # link output files (newer nco forbids + in file names)
    # FIXME: remove all + in pism folders on all computers
    ln -fs $efile $elink

    # concatenate output files and copy history from last file
    ncrcat -O -d time,$extimes -v ${evars// /,} $elink/*-extra.nc $pexfile
    ncrcat -O -d time,$tstimes $elink/*-ts.nc $ptsfile
    ncrcat -O -v timestamp $elink/*-extra.nc $tmsfile
    ncks -A -h -x $elink/y0120000-ts.nc $ptsfile
    ncks -A -h -x $elink/y0120000-extra.nc $pexfile
    ncks -A -h -x $elink/y0120000-extra.nc $tmsfile

    # apply mask and add fill value
    ncap2 -A -s "where(thk<1.0){$(for v in $mvars; do echo -n "$v=-2e9;"; done)};\
    $(for v in $mvars; do echo -n "$v.set_miss(-2e9);"; done)" $pexfile

    # add titles
    prefix="Alpine ice sheet glacial cycle simulations"
    ncatted -h -a title,global,o,c,"$prefix spatial diagnostics" $pexfile
    ncatted -h -a title,global,o,c,"$prefix scalar time series" $ptsfile
    ncatted -h -a title,global,o,c,"$prefix time stamps" $tmsfile

    # remove (mostly) duplicate history, add attributes and compress
    [ "$pp" == "pp" ] && wo="with" || wo="without"
    inst="ETH Zürich, Switzerland and Hokkaido University, Japan"
    subtitle="$res ${rec^^} simulation $wo precipitation reductions"
    for f in $pexfile $ptsfile $tmsfile
    do
        ncatted -h -a author,global,o,c,"Julien Seguinot" $f
        ncatted -h -a history_of_appended_files,global,d,, $f
        ncatted -h -a institution,global,o,c,"$inst" $f
        ncatted -h -a subtitle,global,o,c,"$subtitle" $f
        nccopy -sd1 $f $f.tmp && mv $f.tmp $f
    done

    # remove links
    rm $elink

done
