#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import os
import numpy as np
import pandas as pd
import xarray as xr
import scipy.interpolate as sinterp
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from osgeo import gdal
import util as ut

# geographic projections
utm = ccrs.UTM(32)
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)


def open_dataset(filename):
    """Open single-file dataset with age coordinate."""
    ds = xr.open_dataset(filename, decode_cf=False)
    if 'time' in ds.coords and 'seconds' in ds.time.units:
        ds = ds.assign_coords(time=ds.time/(365*24*60*60))
    if 'time' in ds.coords:
        ds = ds.assign_coords(age=-ds.time)
    return ds


def open_mfdataset(filename):
    """Open multi-file dataset with age coordinate."""
    ds = xr.open_mfdataset(filename, chunks=dict(time=10), decode_cf=False)
    if 'time' in ds.coords and 'seconds' in ds.time.units:
        ds = ds.assign_coords(time=ds.time/(365*24*60*60))
    if 'time' in ds.coords:
        ds = ds.assign_coords(age=-ds.time)
    return ds


def open_subdataset(filename, t, shift=120000, step=500):
    """Open subdataset in multi-file based on format string."""
    ds = open_dataset(filename.format(shift + t + (-t) % step))
    ds = ds.sel(time=t, method='nearest', tolerance=1e-6)
    return ds


def open_visual(filename, t, x, y):
    """Load interpolated output for visualization."""

    # load SRTM bedrock topography
    with open_dataset('../data/external/srtm.nc') as ds:
        srtm = ds.usurf.fillna(0.0) - ds.thk.fillna(0.0)

    # load boot topo
    with open_dataset('../data/processed/alpcyc.1km.in.nc') as ds:
        boot = ds.topg

    # load extra data
    with open_subdataset(filename, t) as ds:
        ds = ds[['thk', 'topg', 'usurf', 'velsurf_mag']]

        # compute ice mask and bedrock uplift
        ds['icy'] = 1.0 * (ds.thk >= 1.0)
        ds['uplift'] = ds.topg - boot

        # interpolate surfaces to axes coords
        ds = ds[['icy', 'uplift', 'usurf', 'velsurf_mag']].interp(x=x, y=y)

    # interpolate srtm topography
    ds['topg'] = srtm.interp(x=x, y=y)

    # correct basal topo for uplift and pop nunataks
    ds['topg'] = ds.topg + ds.uplift.fillna(0.0)
    ds['icy'] = (ds.icy >= 0.5) * (ds.usurf > ds.topg)
    ds['usurf'] = ds.usurf.where(ds.icy)
    ds['velsurf_mag'] = ds.velsurf_mag.where(ds.icy)

    # return interpolated data
    return ds


def open_sealevel(t):
    ds = pd.read_csv('../data/external/spratt2016.txt', comment='#',
                     delimiter='\t', index_col='age_calkaBP').to_xarray()
    ds = ds.SeaLev_shortPC1.dropna('age_calkaBP')
    ds = min(ds.interp(age_calkaBP=-t/1e3, method='cubic').values, 0.0)
    return ds


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


def open_gtif_xarray(filename, extent=None):
    """Open GeoTIFF and return as data array."""
    data, extent = open_gtif(filename, extent=extent)
    x, y = ut.pl.coords_from_extent(extent, *data.shape[::-1])
    da = xr.DataArray(data, coords=dict(x=x, y=y), dims=('y', 'x'))
    return da


def open_shp_coords(filename, ds=1.0):
    """Spline-interpolate coordinates along profile from shapefile."""

    # read profile from shapefile
    filename = os.path.join('..', 'data', 'native', filename)
    shp = shpreader.Reader(filename)
    geom = next(shp.geometries())[0]
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


def open_trimline_data():
    """Open trimline dataset."""

    # read trimlines data
    ds = pd.read_csv('../data/native/trimlines_kelly_etal_2004.csv',
                     index_col='id').to_xarray()

    # convert to UTM 32
    xyz = utm.transform_points(swiss, ds.x.data, ds.y.data, ds.z.data).T
    ds['x'].data, ds['y'].data, ds['z'].data = xyz

    # return dataset
    return ds
