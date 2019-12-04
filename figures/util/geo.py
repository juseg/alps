# Copyright (c) 2016--2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Alps geographic utils.
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import cartowik.naturalearth as cne

# geographic projections
ll = ccrs.PlateCarree()
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)


def draw_lgm_outline(ax=None, alpha=0.75,
                     edgecolor='#e31a1c', facecolor='none'):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=alpha,
                      edgecolor=edgecolor, facecolor=facecolor)
    del shp


def draw_natural_earth(ax=None, mode='gs', **kwargs):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.85' if mode == 'gs' else '#c6ecff'
    cne.add_rivers(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_lakes(ax=ax, edgecolor=edgecolor, facecolor=facecolor, zorder=0, **kwargs)
    cne.add_coastline(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_graticules(ax=ax, interval=1, **kwargs)


def draw_trimlines(ax=None, c='C1', s=4**2, alpha=0.75):
    """Add trimline locations."""
    ax = ax or plt.gca()
    trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                              dtype=None, delimiter=',', names=True)
    ax.scatter(trimlines['x'], trimlines['y'], c=c, s=s, alpha=alpha,
               transform=swiss)
