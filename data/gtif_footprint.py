#!/usr/bin/env python2
# coding: utf-8

import os
import util as ut
import numpy as np

# file paths
runname = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
varname = 'footprint'
ifilepath = ut.alpcyc_bestrun + '/y???????-extra.nc'
ofilepath = 'processed/%s-%s' % (runname, varname)

# read extra output
nc = ut.load(ifilepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]
nc.close()

# compute footprint
footprint = 1 - (thk < 1.0).prod(axis=0)

# make geotiff
levs = [0.5]
ut.make_gtif_shp(x, y, footprint, ofilepath, levs, dtype='byte', epsg=32632,
                 varname=varname)
