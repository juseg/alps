#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import os
import numpy as np
from scipy import ndimage
import pandas as pd
import xarray as xr
import scipy.interpolate as sinterp
import cartopy.crs as ccrs
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
    ds = xr.open_mfdataset(filename, combine='by_coords', chunks=dict(time=10),
                           decode_cf=False)
    if 'time' in ds.coords and 'seconds' in ds.time.units:
        ds = ds.assign_coords(time=ds.time/(365*24*60*60))
    if 'time' in ds.coords:
        ds = ds.assign_coords(age=-ds.time)
    return ds


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
