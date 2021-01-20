#!/usr/bin/env python
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Alps animation tools."""

import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp


# Map elements
# ------------

def draw_major_cities(ax=None, exclude=None, include=None, maxrank=5,
                      textoffset=2, lang='en'):
    """Add major city locations with names."""
    ax = ax or plt.gca()

    # get axes extent
    west, east, south, north = ax.get_extent()

    # relative label positions
    xloc = 'r'  # ('l' if xc < center[0] else 'r')
    yloc = 'u'  # ('l' if yc < center[1] else 'u')
    dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
    dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
    ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
    va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]

    # open shapefile data
    shp = cshp.Reader(cshp.natural_earth(
        resolution='10m', category='cultural', name='populated_places'))

    # loop on records
    for rec in shp.records():
        name = rec.attributes['name_'+lang]
        rank = rec.attributes['SCALERANK']

        # check rank and name
        if rank > maxrank and name not in include or name in exclude:
            continue

        # check location
        geom = rec.geometry
        crs = ccrs.PlateCarree()
        x, y = ax.projection.transform_point(geom.x, geom.y, src_crs=crs)
        if west > x or x > east or south > y or y > north:
            continue

        # plot
        ax.plot(x, y, marker='o', color='0.25', ms=2)
        ax.annotate(name, xy=(x, y), xytext=(dx, dy), color='0.25',
                    textcoords='offset points', ha=ha, va=va, clip_on=True)


# Figure saving
# -------------

def save_animation_frame(func, outdir, t, *args, **kwargs):
    """Save figure produced by func as animation frame if missing."""

    # check if file exists
    fname = os.path.join(outdir, '{:06d}.png').format(t+120000)
    if not os.path.isfile(fname):

        # assemble figure and save
        print('plotting {:s} ...'.format(fname))
        fig = func(t, *args, **kwargs)
        fig.savefig(fname, transparent=True)
        plt.close(fig)
