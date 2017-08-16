#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated geotiffs and shapefiles."""

import os.path
import util as ut
import numpy as np
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
cba = da.from_array(nc.variables['velbase_mag'], chunks=chunks)
dx = x[1] - x[0]
dy = y[1] - y[0]

# create shortcut for ice mask
icy = (thk >= 1.0)

# pseudo mask certain variables (this is a workaround, apparently dask fails
# to perform multiplication on two netCDF variables, posixio assertion failed)
cba[~icy]==0.0

# compute timeseries
print "computing sliding flux..."
slidingflux = cba.sum(axis=(1, 2)).compute()*dx*dy*1e-12  # 1e3 km3/a
print "computing erosion rate..."
erosionrate = 2.7e-7*(cba**2.02).sum(axis=(1, 2)).compute()*dx*dy*1e-9  # m/a

# close extra output
nc.close()

# export timeseries as text files
print "exporting text files..."
prefix = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
prefix = os.path.join('processed', prefix+'-')
np.savetxt(prefix+'erosionrate.txt', np.array((age, erosionrate)).T)
np.savetxt(prefix+'slidingflux.txt', np.array((age, slidingflux)).T)
