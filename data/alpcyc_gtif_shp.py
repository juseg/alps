#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated geotiffs and shapefiles."""

import os.path
import util as ut

# read extra output
filename = ut.alpcyc_bestrun + '/y???????-extra.nc'
nc = ut.load(filename)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(365.0*24*60*60)
thk = nc.variables['thk'][:]
nc.close()

# compute aggregated variables
dt = age[0] - age[1]
duration = (thk >= 1.0).sum(axis=0)*dt
footprint = (duration > 0.0)

# compute deglaciation age
nlastfree = (thk >= 1.0)[::-1].argmax(axis=0)  # number of last free timesteps
deglacage = age[-nlastfree] + dt/2
deglacage[duration==120e3] = age[-1]
deglacage[duration==0.0] = age[0]

# export geotiffs and shapefiles
prefix = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
prefix = os.path.join('processed', prefix+'-')
ut.make_gtif_shp(x, y, deglacage, prefix+'deglacage', range(0, 30001, 1000))
ut.make_gtif_shp(x, y, duration, prefix+'duration', range(50, 120000, 10000))
ut.make_gtif_shp(x, y, footprint, prefix+'footprint', [0.5], dtype='byte')
