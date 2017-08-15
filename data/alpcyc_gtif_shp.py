#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated geotiffs and shapefiles."""

import os.path
import util as ut
import numpy as np

# read extra output
filename = ut.alpcyc_bestrun + '/y???????-extra.nc'
nc = ut.load(filename)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(365.0*24*60*60)
thk = nc.variables['thk'][:]
srf = nc.variables['usurf'][:]
tpa = nc.variables['temppabase'][:]
nc.close()

# compute aggregated variables
dt = age[0] - age[1]
duration = (thk >= 1.0).sum(axis=0)*dt
envelope = srf.max(axis=0)
footprint = (duration > 0.0)
lgmtiming = age[srf.argmax(axis=0)]

# compute deglaciation age
nlastfree = (thk >= 1.0)[::-1].argmax(axis=0)  # number of last free timesteps
deglacage = age[-nlastfree] + dt/2
deglacage[duration==120e3] = age[-1]

# compute duration of temperate ice cover during MIS 2
mis = (age < 29.0) * (age >= 14.0)
warmbased = ((thk[mis] >= 1.0)*(tpa[mis] >= -1e-3)).sum(axis=0)*dt

# apply mask on variables that need one
deglacage = np.ma.masked_where(~footprint, deglacage)
envelope = np.ma.masked_where(~footprint, envelope)
lgmtiming = np.ma.masked_where(~footprint, lgmtiming)

# export geotiffs and shapefiles
prefix = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
prefix = os.path.join('processed', prefix+'-')
ut.make_gtif_shp(x, y, deglacage, prefix+'deglacage', range(0, 30001, 1000))
ut.make_gtif_shp(x, y, duration, prefix+'duration', range(50, 120000, 10000))
ut.make_gtif_shp(x, y, envelope, prefix+'envelope', range(0, 4001, 200))
ut.make_gtif_shp(x, y, footprint, prefix+'footprint', [0.5], dtype='byte')
ut.make_gtif_shp(x, y, lgmtiming, prefix+'lgmtiming', range(21000, 27001, 1000))
ut.make_gtif_shp(x, y, warmbased, prefix+'warmbased', range(0, 15001, 1000))
