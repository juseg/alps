#!/usr/bin/env python2
# coding: utf-8

import os
import numpy as np
import zipfile
from netCDF4 import Dataset
from osgeo import gdal
from osgeo import ogr
from osgeo import osr

# file paths
outdir = os.environ['HOME'] + '/pism/output/0.7.3/'
runbase = 'bern-wc-200m/ramp100a+alplgl1'
varname = 'tempdiff'
ofilepath = 'processed/%s-%s' % (runbase.replace('/', '-'), varname)

# compute stacked extent
stack = -5
offsets = np.arange(-4, 1)
for i, dt in enumerate(offsets):
    runname = 'bern-wc-200m/ramp100acool%04d+alplgl1' % (-100*dt)
    ifilepath = outdir + runname + '/y0002000-extra.nc'
    nc = Dataset(ifilepath)
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    thk = nc.variables['thk'][-1]
    stack = np.where(thk > 1.0, dt, stack)
    nc.close()

# get grid size and origin
cols = len(x)
rows = len(y)
dx = x[1] - x[0]
dy = y[1] - y[0]
x0 = x[0] - dx/2
y0 = y[0] - dy/2
x1 = x[-1] + dx/2
y1 = y[-1] + dy/2

# spatial reference system
srs = osr.SpatialReference()
srs.ImportFromEPSG(32632)

# generate geotiff
driver = gdal.GetDriverByName('GTiff')
rast = driver.Create(ofilepath + '.tif', cols, rows, 1, gdal.GDT_Float32)
rast.SetGeoTransform((x0, dx, 0, y1, 0, -dy))
rast.SetProjection(srs.ExportToWkt())
band = rast.GetRasterBand(1)
band.WriteArray(np.flipud(stack.T))
band.ComputeStatistics(0)
band.FlushCache()

# generate contours
#ContourGenerate(Band srcBand, double contourInterval, double contourBase,
#                int fixedLevelCount, int useNoData, double noDataValue,
#                OGRLayerShadow * dstLayer, int idField, int elevField,
#                GDALProgressFunc callback=0, void * callback_data=None)
driver = ogr.GetDriverByName('ESRI Shapefile')
shp = driver.CreateDataSource('.')
lyr = shp.CreateLayer(ofilepath, srs, ogr.wkbLineString)
f0_defn = ogr.FieldDefn('id', ogr.OFTInteger)
f0 = lyr.CreateField(f0_defn)
f1_defn = ogr.FieldDefn(varname, ogr.OFTReal)
f1 = lyr.CreateField(f1_defn)
gdal.ContourGenerate(band, 0, 0, np.append(offsets, 1)-0.5, 0, 0, lyr, f0, f1)
lyr.SyncToDisk()

# close datasets
lyr = shp = None
band = rast = None

# create zip archive
with zipfile.ZipFile(ofilepath + '.zip', 'w') as zf:
    extensions = ['dbf', 'prj', 'shp', 'shx', 'tif']
    for f in [ofilepath + '.' + ext for ext in extensions]:
        zf.write(f, arcname=os.path.basename(f))
    zf.close()
