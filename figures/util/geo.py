# Copyright (c) 2016--2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Alps geographic utils.
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import cartowik.naturalearth as cne
import util

# geographic projections
ll = ccrs.PlateCarree()
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)


def draw_boot_topo(ax=None, filename='alpcyc.1km.in.nc'):
    """Add bootstrapping topography image."""
    ax = ax or plt.gca()
    # FIXME use upcoming pism paleo kit
    with util.io.open_dataset('../data/processed/'+filename) as ds:
        im = (ds.topg/1e3).plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                                       vmin=0.0, vmax=3.0, zorder=-1)
    return im


def draw_cpu_grid(ax=None, extent='alps', nx=24, ny=24):
    """Add CPU partition grid."""
    ax = ax or plt.gca()
    w, e, s, n = util.fig.regions[extent]
    x = np.linspace(w, e, 24)
    y = np.linspace(s, n, 24)
    xx, yy = np.meshgrid(x, y)
    vlines = list(np.array([xx, yy]).T)
    hlines = list(np.array([xx.T, yy.T]).T)
    lines = hlines + vlines
    props = dict(color='k', linewidths=0.25, linestyles=':')
    lcoll = mpl.collections.LineCollection(lines, **props)
    ax.add_collection(lcoll)


def draw_lgm_outline(ax=None, alpha=0.75,
                     edgecolor='#e31a1c', facecolor='none'):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=alpha,
                      edgecolor=edgecolor, facecolor=facecolor)
    del shp


def draw_model_domain(ax=None, extent='alps'):
    """Add Rhine lobe scaling domain."""
    w, e, s, n = util.fig.regions[extent]
    x = [w, e, e, w, w]
    y = [s, s, n, n, s]
    ax.plot(x, y, c='k', lw=0.5)


def draw_natural_earth(ax=None, mode='gs', **kwargs):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.85' if mode == 'gs' else '#c6ecff'
    cne.add_rivers(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_lakes(ax=ax, edgecolor=edgecolor, facecolor=facecolor, zorder=0,
                  **kwargs)
    cne.add_coastline(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_graticules(ax=ax, interval=1, **kwargs)


def draw_trimlines(ax=None, c='C1', s=4**2, alpha=0.75):
    """Add trimline locations."""
    ax = ax or plt.gca()
    trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                              dtype=None, delimiter=',', names=True)
    ax.scatter(trimlines['x'], trimlines['y'], c=c, s=s, alpha=alpha,
               transform=swiss)
