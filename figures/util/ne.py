#!/usr/bin/env python2
# coding: utf-8

"""Natural Earth Data and Swisstopo hydrology."""

import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp
import cartowik.naturalearth as cne
import util as ut


# Geographic data
# ---------------

# geographic projections
ll = ccrs.PlateCarree()


# Map elements
# ------------

# FIXME move this to another submodule
def draw_natural_earth(ax=None, mode='gs', **kwargs):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.85' if mode == 'gs' else '#c6ecff'
    cne.add_rivers(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_lakes(ax=ax, edgecolor=edgecolor, facecolor=facecolor, zorder=0, **kwargs)
    cne.add_coastline(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_graticules(ax=ax, interval=1, **kwargs)
