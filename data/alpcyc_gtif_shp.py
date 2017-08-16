#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated geotiffs and shapefiles."""

import os.path
import util as ut
import numpy as np
import dask
import dask.array as da

# chunk size
chunks = (1000, 601, 901)

# read extra output
print "reading extra output..."
filename = ut.alpcyc_bestrun + '/y???????-extra.nc'
nc = ut.load(filename)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(365.0*24*60*60)
thk = da.from_array(nc.variables['thk'], chunks=chunks)
srf = da.from_array(nc.variables['usurf'], chunks=chunks)
tpa = da.from_array(nc.variables['temppabase'], chunks=chunks)
cba = da.from_array(nc.variables['velbase_mag'], chunks=chunks)
dt = age[0] - age[1]

# create shortcut for ice mask
icy = (thk >= 1.0)

# pseudo mask certain variables (this is a workaround, apparently dask fails
# to perform multiplication on two netCDF variables, posixio assertion failed)
cba[~icy]==0.0
tpa[~icy]==-99.0

# compute aggregated variables
print "computing deglaciation age..."
deglacage = age[-icy[::-1].argmax(axis=0).compute()]
print "computing ice cover duration..."
duration = icy.sum(axis=0).compute()*dt
print "computing surface envelope..."
envelope = srf.max(axis=0).compute()
print "computing total erosion..."
erosion = 2.7e-7*(cba**2.02).sum(axis=0).compute()*dt*1e3  # (Herman et al, 2015)
print "computing number of glaciations..."
nadvances = (icy[0] + (icy[1:]-icy[:-1]).sum(axis=0) + icy[-1]).compute()/2
print "computing last glacial maximum timing..."
lgmtiming = age[srf.argmax(axis=0).compute()]
print "computing maximum ice thickness"
maxicethk = thk.max(axis=0).compute()
print "computing MIS2 warm-based ice cover..."
mis2 = (age < 29.0) * (age >= 14.0)
mis2print = ~icy[mis2].prod(axis=0).compute()
warmbased = (tpa[mis2] >= -1e-3).sum(axis=0).compute()*dt

# compute derived variables
print "computing footprint..."
footprint = (duration > 0.0)
modernice = (duration == 120.0)

# close extra output
nc.close()

# apply mask on variables that need one
print "applying masks..."
deglacage = np.ma.masked_where(~footprint+modernice, deglacage)
envelope = np.ma.masked_where(~footprint, envelope)
erosion = np.ma.masked_where(~footprint, erosion)
lgmtiming = np.ma.masked_where(~footprint, lgmtiming)
warmbased = np.ma.masked_where(~mis2print, warmbased)

# export geotiffs and shapefiles
print "exporting geotiffs..."
prefix = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
prefix = os.path.join('processed', prefix+'-')
ut.make_gtif_shp(x, y, deglacage, prefix+'deglacage', range(0, 30001, 1000))
ut.make_gtif_shp(x, y, duration, prefix+'duration', range(0, 120001, 10000))
ut.make_gtif_shp(x, y, erosion, prefix+'erosion', [0.1, 1, 10, 100, 1000])
ut.make_gtif_shp(x, y, envelope, prefix+'envelope', range(0, 4001, 200))
ut.make_gtif_shp(x, y, footprint, prefix+'footprint', [0.5], dtype='byte')
ut.make_gtif_shp(x, y, lgmtiming, prefix+'lgmtiming', range(21000, 27001, 1000))
ut.make_gtif_shp(x, y, nadvances, prefix+'nadvances', range(13), dtype='byte')
ut.make_gtif_shp(x, y, maxicethk, prefix+'maxicethk', range(0, 4001, 200))
ut.make_gtif_shp(x, y, warmbased, prefix+'warmbased', range(0, 15001, 1000))
