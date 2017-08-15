#!/usr/bin/env python2
# coding: utf-8

import os
import util as ut
import numpy as np
import zipfile

# file paths
runname = '-'.join(map(os.path.basename, os.path.split(ut.alpcyc_bestrun)))
varname = 'deglacage'
ifilepath = ut.alpcyc_bestrun + '/y???????-extra.nc'
ofilepath = 'processed/%s-%s' % (runname, varname)

# read extra output
nc = ut.load(ifilepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(365.0*24*60*60)
thk = nc.variables['thk'][:]
nc.close()

# compute deglaciation age
icy = (thk >= 1.0)
nlastfree = icy[::-1].argmax(axis=0)  # number of last free timesteps
deglacage = (age[-nlastfree-1]+age[-nlastfree]) / 2

# fill in always and never icy cases
nevericy = (nlastfree == 0)*(icy[-1] == 0)
alwaysicy = (nlastfree == 0)*(icy[-1] == 1)
deglacage[alwaysicy] = age[-1]
deglacage[nevericy] = age[0]

# make geotiff
ut.make_gtif_shp(x, y, deglacage, ofilepath, dtype='float32', epsg=32632,
                 varname=varname, interval=0, base=0, levels=range(0, 30001, 1000))

# create zip archive
with zipfile.ZipFile(ofilepath + '.zip', 'w') as zf:
    extensions = ['dbf', 'prj', 'shp', 'shx', 'tif']
    for f in [ofilepath + '.' + ext for ext in extensions]:
        zf.write(f, arcname=os.path.basename(f))
    zf.close()
