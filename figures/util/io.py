#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import pandas as pd
import cartopy.crs as ccrs

# geographic projections
utm = ccrs.UTM(32)
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)


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
