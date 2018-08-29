#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import iceplotlib.plot as iplt
import os
import numpy as np
import xarray as xr
import scipy.interpolate as sinterp
import cartopy.io.shapereader as shpreader
from osgeo import gdal


def load(filepath):
    """Load file relative to PISM directory."""

    filepath = os.path.join(os.environ['HOME'], 'pism', filepath)
    return iplt.load(filepath)


def load_mfoutput(filepath):
    """Load multi-file output data."""
    filepath = os.path.join(os.environ['HOME'], 'pism', filepath)
    ds = xr.open_mfdataset(filepath, concat_dim='time', chunks=dict(time=10),
                           decode_cf=False, decode_times=False)
    if 'time' in ds.coords:
        ds = ds.assign_coords(age=-ds.time/(1e3*365*24*60*60))
    if 'time' in ds.dims:
        ds = ds.swap_dims(dict(time='age'))
    return ds


def load_postproc(filename):
    """Load post-processed netcdf data."""
    filepath = os.path.join('..', 'data', 'processed', filename)
    ds = xr.open_dataset(filepath, decode_times=False)
    if 'time' in ds.coords:
        ds = ds.assign_coords(age=-ds.time/(1e3*365*24*60*60))
    if 'time' in ds.dims:
        ds = ds.swap_dims(dict(time='age'))
    return ds


def load_postproc_txt(runpath, varname):
    """Load post-processed text data."""

    runpath = runpath.rstrip('/')
    prefix = '-'.join(map(os.path.basename, os.path.split(runpath)))
    prefix = os.path.join('..', 'data', 'processed', prefix+'-ts-')
    filename = prefix + varname + '.txt'
    age, z = np.loadtxt(filename, unpack=True)
    return age, z


def open_gtif(filename, extent=None):
    """Open GeoTIFF and return data and extent."""

    # open dataset
    ds = gdal.Open(filename)

    # read geotransform
    x0, dx, dxdy, y0, dydx, dy = ds.GetGeoTransform()
    assert dxdy == dydx == 0.0  # rotation parameters should be zero

    # if extent argument was not given
    if extent is None:

        # set image indexes to cover whole image
        col0 = 0  # index of first (W) column
        row0 = 0  # index of first (N) row
        cols = ds.RasterXSize  # number of cols to read
        rows = ds.RasterYSize  # number of rows to read

    # if extent argument was given
    else:

        # compute image indexes corresponding to map extent
        w, e, s, n = extent
        col0 = int((w-x0)/dx)  # index of first (W) column
        row0 = int((n-y0)/dy)  # index of first (N) row
        col1 = int((e-x0)/dx) + 1  # index of last (E) column
        row1 = int((s-y0)/dy) + 1  # index of last (S) row

        # make sure indexes are within data extent
        col0 = max(0, col0)
        row0 = max(0, row0)
        col1 = min(ds.RasterXSize, col1)
        row1 = min(ds.RasterYSize, row1)

        # compute number of cols and rows needed
        cols = col1 - col0  # number of cols needed
        rows = row1 - row0  # number of rows needed

        # compute coordinates of new origin
        x0 = x0 + col0*dx
        y0 = y0 + row0*dy

    # compute new image extent
    x1 = x0 + dx*cols
    y1 = y0 + dy*rows

    # read image data
    data = ds.ReadAsArray(col0, row0, cols, rows)

    # convert to masked array if dataset has nodata value
    ndval = ds.GetRasterBand(1).GetNoDataValue()
    if ndval is not None:
        data = np.ma.masked_equal(data, ndval)

    # close dataset and return image data and extent
    ds = None
    return data, (x0, x1, y0, y1)


def open_shp_coords(filename, ds=1.0):
    """Spline-interpolate coordinates along profile from shapefile."""

    # read profile from shapefile
    filename = os.path.join('..', 'data', 'native', filename)
    shp = shpreader.Reader(filename)
    geom = shp.geometries().next()[0]
    x, y = np.array(geom).T
    del shp, geom

    # compute distance along profile
    d = ((np.diff(x)**2+np.diff(y)**2)**0.5).cumsum()/1e3
    d = np.insert(d, 0, 0.0)

    # spline-interpolate profile
    s = np.arange(0.0, d[-1], ds)
    x = sinterp.spline(d, x, s)
    y = sinterp.spline(d, y, s)
    d = s

    # build coordinate xarrays
    x = xr.DataArray(x, coords=[d], dims='d')
    y = xr.DataArray(y, coords=[d], dims='d')

    # return coordinates
    return x, y
