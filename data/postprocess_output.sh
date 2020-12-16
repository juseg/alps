#!/bin/bash
# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Postprocess output files if older than scripts
# ----------------------------------------------

# ALPCYC aggregated variables
for ofile in alpcyc.{1km.epic.pp,2km.{epic,grip,md01}.{cp,pp}}.agg.nc
do
    [ $ofile -ot postprocess_alpcyc_agg.py ] && ./postprocess_alpcyc_agg.py
done

# ALPCYC continuous variables
for ofile in alpcyc.{1km.epic.pp,2km.{epic,grip,md01}.{cp,pp}}.{dt,ex.1ka,tms,ts.10a}.nc
do
    [ $ofile -ot postprocess_alpcyc_cts.py ] && ./postprocess_alpcyc_cts.py
done

# ALPCYC input files
for ofile in alpcyc.{1km,2km}.in.nc
do
    [ $ofile -ot postprocess_alpcyc_inp.sh ] && ./postprocess_alpcyc_inp.sh
done

# ALPERO aggregated variables
for ofile in alpero.{1km.epic.pp,2km.{epic,grip,md01}.{cp,pp}}.agg.nc
do
    [ $ofile -ot postprocess_alpero_agg.py ] && ./postprocess_alpero_agg.py
done

# ALPERO continuous variables
for ofile in alpero.{1km.epic.pp,2km.{epic,grip,md01}.{cp,pp}}.cts.nc
do
    [ $ofile -ot postprocess_alpero_cts.py ] && ./postprocess_alpero_cts.py
done
