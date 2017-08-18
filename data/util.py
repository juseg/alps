#!/usr/bin/env python2
# coding: utf-8

"""Data processing methods."""

import os
import zipfile
import numpy as np
import netCDF4 as nc4
from osgeo import gdal
from osgeo import ogr
from osgeo import osr


# Alps cycle parameters
# ---------------------

alpcyc_bestrun = 'output/e9d2d1f/alps-wcnn-1km/epica3222cool1220+alpcyc4+pp'


# Input and output methods
# ------------------------

def load(filepath):
    """Load file relative to PISM directory."""

    filepath = os.path.join(os.environ['HOME'], 'pism', filepath)
    return nc4.MFDataset(filepath)


def make_gtif_shp(x, y, z, filename, levels, dtype='float32', epsg=32632,
                  varname='z', ndval=-9999.0):
    """Make geotiff and shapefile from given coords and masked array."""

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
    srs.ImportFromEPSG(epsg)

    # generate geotiff
    driver = gdal.GetDriverByName('GTiff')
    gdtype = gdal.GetDataTypeByName(dtype)
    rast = driver.Create(filename + '.tif', cols, rows, 1, gdtype)
    rast.SetGeoTransform((x0, dx, 0, y1, 0, -dy))
    rast.SetProjection(srs.ExportToWkt())
    band = rast.GetRasterBand(1)
    if np.ma.isMaskedArray(z):
        band.SetNoDataValue(ndval)
        z = z.filled(ndval)
    band.WriteArray(z[::-1])
    band.FlushCache()

    # generate contours
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.CreateDataSource('.')
    lyr = shp.CreateLayer(filename, srs, ogr.wkbLineString)
    f0_defn = ogr.FieldDefn('id', ogr.OFTInteger)
    f0 = lyr.CreateField(f0_defn)
    dtype = ogr.OFTReal
    f1_defn = ogr.FieldDefn(varname, ogr.OFTReal)
    f1 = lyr.CreateField(f1_defn)
    gdal.ContourGenerate(band, 0, 0, levels, 0, 0, lyr, f0, f1)

    # close datasets
    band = rast = None
    lyr = shp = None


def make_zip(filename):
    """Make zip file containing all processed data."""

    # create zip archive
    with zipfile.ZipFile(filename + '.zip', 'w') as zf:
        extensions = ['dbf', 'prj', 'shp', 'shx', 'tif']
        for f in [filename + '.' + ext for ext in extensions]:
            zf.write(f, arcname=os.path.basename(f))
