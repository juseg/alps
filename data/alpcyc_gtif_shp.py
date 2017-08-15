#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated geotiffs and shapefiles."""

import os
import util as ut
import numpy as np

# output files prefix
prefix = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
prefix = os.path.join('processed', prefix+'-')

# read extra output
print 'reading extra output...'
filename = ut.alpcyc_bestrun + '/y???????-extra.nc'
nc = ut.load(filename)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(365.0*24*60*60)
thk = nc.variables['thk'][:]
nc.close()

# compute deglaciation age
print 'computing deglaciation age...'
icy = (thk >= 1.0)
nlastfree = icy[::-1].argmax(axis=0)  # number of last free timesteps
deglacage = (age[-nlastfree-1]+age[-nlastfree]) / 2

# fill in always and never icy cases
nevericy = (nlastfree == 0)*(icy[-1] == 0)
alwaysicy = (nlastfree == 0)*(icy[-1] == 1)
deglacage[alwaysicy] = age[-1]
deglacage[nevericy] = age[0]

# file paths
varname = 'deglacage'
ofilepath = prefix + varname

# make geotiff
levs = np.arange(0e3, 30e3+1, 1e3)
ut.make_gtif_shp(x, y, deglacage, ofilepath, levs, dtype='float32', epsg=32632,
                 varname=varname)

# ----

# compute duration of ice cover
print 'computing duration of ice cover...'
duration = (thk >= 1.0).sum(axis=0)*100.0

# file paths
varname = 'duration'
ofilepath = prefix + varname

# make geotiff
levs = np.arange(50.0, 120e3, 10e3)
ut.make_gtif_shp(x, y, duration, ofilepath, levs, dtype='float32', epsg=32632,
                 varname=varname)

# ----

# compute footprint
print 'computing footprint...'
footprint = 1 - (thk < 1.0).prod(axis=0)

# file paths
varname = 'footprint'
ofilepath = prefix + varname

# make geotiff
levs = [0.5]
ut.make_gtif_shp(x, y, footprint, ofilepath, levs, dtype='byte', epsg=32632,
                 varname=varname)
