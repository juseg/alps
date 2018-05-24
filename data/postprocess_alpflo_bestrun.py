#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated geotiffs, shapefiles and text files."""

import os.path
import netCDF4 as nc4
import util as ut
import numpy as np

# read extra output
print "reading extra output..."
filename = ut.alpflo_bestrun + '/y0095480-extra.nc'
filepath = os.path.join(os.environ['HOME'], 'pism', filename)
nc = nc4.Dataset(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(365.0*24*60*60)
h = nc.variables['thk']
s = nc.variables['usurf']
u = nc.variables['uvelsurf']
v = nc.variables['vvelsurf']
c = nc.variables['velsurf_mag']

# extract time slices
lgmage = 24558.583333333332 # max of slvol
lgmage = 24533.583333333332 # max of ice_area_glacierized
lgmidx = abs(age-lgmage).argmin()
lgmage = age[lgmidx]
lgmicethk = h[lgmidx]
lgmicesrf = s[lgmidx]
lgmsrfvel = c[lgmidx]

# close extra output
nc.close()

# apply mask on variables that need one
print "applying masks..."
lgmicethk = np.ma.masked_where(lgmicethk<1.0, lgmicethk)
lgmicesrf = np.ma.masked_where(lgmicethk<1.0, lgmicesrf)
lgmsrfvel = np.ma.masked_where(lgmicethk<1.0, lgmsrfvel)

# export geotiffs and shapefiles
print "exporting geotiffs..."
prefix = '-'.join(map(os.path.basename, os.path.split(ut.alpflo_bestrun)))
prefix = os.path.join('processed', prefix+'-')
ut.make_gtif_shp(x, y, lgmicethk, prefix+'lgmicethk', range(0, 5001, 100))
ut.make_gtif_shp(x, y, lgmicesrf, prefix+'lgmicesrf', range(0, 5001, 100))
ut.make_gtif_shp(x, y, lgmsrfvel, prefix+'lgmsrfvel', [1, 10, 100, 1000])
