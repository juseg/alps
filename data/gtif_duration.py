#!/usr/bin/env python2
# coding: utf-8

import os
import util as ut
import numpy as np

# file paths
runname = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
varname = 'duration'
ifilepath = ut.alpcyc_bestrun + '/y???????-extra.nc'
ofilepath = 'processed/%s-%s' % (runname, varname)

# read extra output
nc = ut.load(ifilepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]
nc.close()

# compute duration of ice cover
duration = (thk >= 1.0).sum(axis=0)*100.0

# make geotiff
levs = np.arange(50.0, 120e3, 10e3)
ut.make_gtif_shp(x, y, duration, ofilepath, levs, dtype='float32', epsg=32632,
                 varname=varname)
