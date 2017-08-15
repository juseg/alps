#!/usr/bin/env python2
# coding: utf-8

import os
import util as ut
import numpy as np
import zipfile

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
ut.make_gtif_shp(x, y, footprint, ofilepath, dtype='byte', epsg=32632,
                 varname=varname, interval=1.0, base=0.5, levels=None)

# create zip archive
with zipfile.ZipFile(ofilepath + '.zip', 'w') as zf:
    extensions = ['dbf', 'prj', 'shp', 'shx', 'tif']
    for f in [ofilepath + '.' + ext for ext in extensions]:
        zf.write(f, arcname=os.path.basename(f))
    zf.close()
