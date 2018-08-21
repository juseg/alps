#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated variables."""

import os
import sys
import datetime
import xarray as xr


# Load model output
# -----------------

# load extra output
print "loading extra output..."
ex = xr.open_mfdataset(os.environ['HOME']+'/pism/output/e9d2d1f/alps-wcnn-1km/'
                       'epica3222cool1220+alpcyc4+pp/y???????-extra.nc',
                       chunks={'time': 50}, decode_times=False, decode_cf=True)

# create age coordinate and extract time step
ex['age'] = -ex['time']/(365.0*24*60*60)
dt = ex['age'][0] - ex['age'][1]

# init postprocessed dataset with global attributes
pp = xr.Dataset(attrs=ex.attrs)
pp.attrs['title'] = 'Alpine ice sheet glacial cycle simulations aggregated variables'
pp.attrs['institution'] = 'ETH Zürich, Switzerland; Hokkaido University, Japan'
pp.attrs['command'] = '{user}@{host} {time}: {cmdl}\n'.format(
    user=os.environ['USER'], host=os.uname()[1], cmdl=' '.join(sys.argv),
    time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
pp.attrs['history'] = pp.attrs['command'] + pp.attrs['history']


# Prepare max extent snapshot variables
# -------------------------------------

# compute index of max extent
a = 24556.0  # max of slvol and volume_glacierized
a = 24568.0  # max of area_glacierized
i = abs(ex.age-a).argmin()  # could also use ex.sel()

# compute max extent variables
ln = 'maximum extent ice thickness'
print "computing " + ln + "..."
pp['maxextthk'] = ex.thk[i]
pp['maxextthk'] = pp.maxextthk.where(pp.maxextthk>=1.0)
pp['maxextthk'].attrs = dict(long_name=ln, units=ex.thk.units)
ln = 'maximum extent bedrock topography'
print "computing " + ln + "..."
pp['maxexttpg'] = ex.topg[i]
pp['maxexttpg'].attrs = dict(long_name=ln, units=ex.topg.units)
ln = 'maximum extent ice surface elevation'
print "computing " + ln + "..."
pp['maxextsrf'] = ex.usurf[i].where(pp.maxextthk>=1.0)
pp['maxextsrf'].attrs = dict(long_name=ln, units=ex.usurf.units)
# FIXME {b,s}{vx,vy,vn,tp,tt}?


# Prepare max thickness transgressive variables
# ---------------------------------------------

ln = 'maximum ice thickness age'
print "computing " + ln + "..."
i = ex['thk'].argmax(axis=0).compute()
pp['maxthkage'] = ex.age[i].compute()
pp['maxthkage'].attrs = dict(long_name=ln, units='years')
ln = 'maximum ice thickness'
print "computing " + ln + "..."
pp['maxthkthk'] = ex.thk[i].compute()
pp['maxthkage'] = pp.maxthkage.where(pp.maxthkthk>=1.0)
pp['maxthkthk'] = pp.maxthkthk.where(pp.maxthkthk>=1.0)
pp['maxthkthk'].attrs = dict(long_name=ln, units=ex.thk.units)
ln = 'maximum ice thickness surface elevation'
print "computing " + ln + "..."
pp['maxthksrf'] = ex.usurf[i].compute().where(pp.maxthkthk>=1.0)
pp['maxthksrf'].attrs = dict(long_name=ln, units=ex.usurf.units)
# FIXME {b,s}{vx,vy,vn,tp,tt}?


# Prepare glacial cycle integrated variables
# ------------------------------------------

ln = 'ice cover duration'
print "computing " + ln + "..."
pp['covertime'] = (ex.thk>=1.0).sum(axis=0)*dt
pp['covertime'].attrs = dict(long_name=ln, units='years')
ln = 'deglaciation age'
print "computing " + ln + "..."
i = (ex.thk>=1.0)[::-1].argmax(axis=0).compute()
pp['deglacage'] = ex.age[-i].where(i>0)
pp['deglacage'].attrs = dict(long_name=ln, units='years')
ln = 'ice cover footprint'
print "computing " + ln + "..."
pp['footprint'] = (pp.covertime > 0.0)
pp['footprint'].attrs = dict(long_name=ln, units='')


# Export aggregated data
# ----------------------

# create directory if missing
if not os.path.exists('processed'):
    os.makedirs('processed')

# export to netcdf
print "exporting aggregated data..."
pp = pp.drop('time')
pp.to_netcdf('processed/alpcyc.1km.epic.pp.aggregated.nc', mode='w',
             encoding={var: {'zlib': True, 'shuffle': True, 'complevel':5}
                       for var in pp.variables})

# close datasets
ex.close()
pp.close()
