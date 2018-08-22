#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated variables."""

import os
import sys
import datetime
import xarray as xr


# Variable names
# --------------

# mapping between 3-char variable names and pism variable names
pism_names = dict(age='age', btp='temppabase', btt='tempicethk_basal',
                  bvn='velbase_mag', bvx='uvelbase', bvy='vvelbase',
                  svn='velsurf_mag', svx='uvelsurf', svy='vvelsurf',
                  thk='thk', tpg='topg', srf='usurf')

# mapping between 3-char variable names and long names in output file
long_names = dict(age='age',
                  btp='pressure-adjuste basal temperature',
                  btt='basal temperate ice layer thickness',
                  bvn='basal velocity norm',
                  bvx='basal velocity x-component',
                  bvy='basal velocity y-component',
                  svn='surface velocity norm',
                  svx='surface velocity x-component',
                  svy='surface velocity y-component',
                  srf='ice surface elevation',
                  thk='ice thickness',
                  tpg='basal topography')


# Load model output
# -----------------

# load extra output
print "loading extra output..."
ex = xr.open_mfdataset(os.environ['HOME']+'/pism/output/e9d2d1f/alps-wcnn-1km/'
                       'epica3222cool1220+alpcyc4+pp/y???????-extra.nc',
                       chunks={'time': 50}, decode_times=False, decode_cf=True)

# get global attributes from last file (netcdf4 issue #835)
last = xr.open_dataset(os.environ['HOME']+'/pism/output/e9d2d1f/alps-wcnn-1km/'
                     'epica3222cool1220+alpcyc4+pp/y0120000-extra.nc')
ex.attrs = last.attrs
last.close()

# create age coordinate and extract time step
ex['age'] = -ex['time']/(365.0*24*60*60)
ex['age'].attrs['units'] = 'years'
dt = ex['age'][0] - ex['age'][1]
ex = ex.drop('time')

# init postprocessed dataset with global attributes
pp = xr.Dataset(attrs=ex.attrs)
pp.attrs['title'] = ('Alpine ice sheet glacial cycle simulations '
                     'aggregated variables')
pp.attrs['author'] = 'Julien Seguinot'
pp.attrs['institution'] = ('ETH Zürich, Switzerland and '
                           'Hokkaido University, Japan')
pp.attrs['command'] = '{user}@{host} {time}: {cmdl}\n'.format(
    user=os.environ['USER'], host=os.uname()[1], cmdl=' '.join(sys.argv),
    time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
pp.attrs['history'] = pp.attrs['command'] + pp.attrs['history']
pp.attrs['comment'] = """Aggregated dataset contents:
* Maximum extent (maxext*) variables correspond to a model output snapshot at
  24.57 ka before present, which is the age of maximum glacierized area.
* Maximum thickness (maxthk*) variables are time-transgressive and correspond
  to the age of maximum ice thickness in each grid cell, given by the maximum
  thickness age (maxthkage) variable.
* Other variables are numerically integrated from 119.99 to 0.0 ka with a
  temporal resolution of 10 a.
"""

# copy pism configuration parameters
pp['pism_config'] = ex.pism_config


# Prepare max extent snapshot variables
# -------------------------------------

# compute index of max extent
a = 24556.0  # max of slvol and volume_glacierized
a = 24568.0  # max of area_glacierized
i = abs(ex.age-a).argmin()  # could also use ex.sel()

# compute max extent variables
for var in ['thk', 'btp', 'btt', 'bvx', 'bvy', 'srf', 'svx', 'svy', 'tpg']:
    ln = 'maximum extent ' + long_names[var]
    print "computing " + ln + "..."
    pp['maxext'+var] = ex[pism_names[var]][i].compute()
    if var != 'tpg':
        pp['maxext'+var] = pp['maxext'+var].where(pp.maxextthk >= 1.0)
    pp['maxext'+var].attrs = dict(long_name=ln, units=pp['maxext'+var].units)


# Prepare max thickness transgressive variables
# ---------------------------------------------

# compute index of max thickness
print "computing index of maximum ice thickness..."
i = ex['thk'].argmax(axis=0).compute()

# compute max thickness variables
for var in ['thk', 'age', 'btp', 'btt', 'bvn', 'srf']:
    ln = 'maximum thickness ' + long_names[var]
    print "computing " + ln + "..."
    pp['maxthk'+var] = ex[pism_names[var]][i].compute()
    pp['maxthk'+var] = pp['maxthk'+var].where(pp.maxthkthk >= 1.0)
    pp['maxthk'+var].attrs = dict(long_name=ln, units=pp['maxthk'+var].units)


# Prepare glacial cycle integrated variables
# ------------------------------------------

ln = 'ice cover duration'
print "computing " + ln + "..."
pp['covertime'] = (ex.thk >= 1.0).sum(axis=0).compute()*dt
pp['covertime'].attrs = dict(long_name=ln, units='years')
ln = 'deglaciation age'
print "computing " + ln + "..."
i = (ex.thk >= 1.0)[::-1].argmax(axis=0).compute()
pp['deglacage'] = ex.age[-i].where(i > 0)
pp['deglacage'].attrs = dict(long_name=ln, units='years')
ln = 'ice cover footprint'
print "computing " + ln + "..."
pp['footprint'] = (pp.covertime > 0.0).compute()
pp['footprint'].attrs = dict(long_name=ln, units='')


# Export aggregated data
# ----------------------

# create directory if missing
if not os.path.exists('processed'):
    os.makedirs('processed')

# export to netcdf
print "exporting aggregated data..."
pp.to_netcdf('processed/alpcyc.1km.epic.pp.agg.nc', mode='w',
             encoding={var: {'zlib': True, 'shuffle': True, 'complevel': 5}
                       for var in pp.variables})

# close datasets
ex.close()
pp.close()
