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
runname = 'alps-wcnn-1km/epica3222cool0950+acyc1+esia5'
varname = 'footprint'
ifilepath = outdir + runname + '/extra.nc'
ofilepath = 'processed/%s-%s' % (runname.replace('/', '-'), varname)

# read extra output
nc = Dataset(ifilepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]
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

# compute footprint
footprint = 1 - (thk < 1.0).prod(axis=0)

# spatial reference system
srs = osr.SpatialReference()
srs.ImportFromEPSG(32632)

# generate geotiff
driver = gdal.GetDriverByName('GTiff')
rast = driver.Create(ofilepath + '.tif', cols, rows, 1, gdal.GDT_Byte)
rast.SetGeoTransform((x0, dx, 0, y1, 0, -dy))
rast.SetProjection(srs.ExportToWkt())
band = rast.GetRasterBand(1)
band.WriteArray(np.flipud(footprint.T))
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
f1_defn = ogr.FieldDefn(varname, ogr.OFTInteger)
f1 = lyr.CreateField(f1_defn)
gdal.ContourGenerate(band, 1.0, 0.5, [], 0, 0, lyr, f0, f1)

# close datasets
lyr = shp = None
band = rast = None

# create zip archive
with zipfile.ZipFile(ofilepath + '.zip', 'w') as zf:
    extensions = ['dbf', 'prj', 'shp', 'shx', 'tif']
    for f in [ofilepath + '.' + ext for ext in extensions]:
        zf.write(f, arcname=os.path.basename(f))
    zf.close()
