# Copyright (c) 2016--2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Alps project mapping tools.
"""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import cartowik.naturalearth as cne
import util

# geographic projections
ll = ccrs.PlateCarree()


def draw_boot_topo(ax=None, filename='alpcyc.1km.in.nc'):
    """Add bootstrapping topography image."""
    ax = ax or plt.gca()
    # FIXME use upcoming pism paleo kit
    with xr.open_dataset('../data/processed/'+filename) as ds:
        im = (ds.topg/1e3).plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                                       vmin=0.0, vmax=3.0, zorder=-1)
    return im


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
