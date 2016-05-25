#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import numpy as np
import iceplotlib.plot as iplt
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# cartopy features
rivers = cfeature.NaturalEarthFeature(
    category='physical', name='rivers_lake_centerlines', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.5)
lakes = cfeature.NaturalEarthFeature(
    category='physical', name='lakes', scale='10m',
    edgecolor='0.25', facecolor='0.85', lw=0.25)
coastline = cfeature.NaturalEarthFeature(
    category='physical', name='coastline', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.25)
graticules = cfeature.NaturalEarthFeature(
    category='physical', name='graticules_1', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.1)

# initialize figure
figw, figh = 135.01, 80.01
fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=ccrs.UTM(32),
                           left=2.5, right=20.0, bottom=2.5, top=2.5)
cax = fig.add_axes([1-17.5/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])
ax.set_rasterization_zorder(2.5)

# load extra data
filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-1km/'
            'epica3222cool0950+acyc1+esia5/y???????-extra.nc')
nc = iplt.load(filepath)
w, e, s, n = 125, 425, 300, 500  # Swiss foreland
w, e, s, n = 000, 901, 000, 601  # Whole domain
x = nc.variables['x'][w:e]
y = nc.variables['y'][s:n]
thk = nc.variables['thk'][:, w:e, s:n]

# compute footprint
icy = (thk >= 1.0)

# filter out short glaciations
#icysum = icy.cumsum(axis=0)
#icy = (icysum[5:] - icysum[:-5])/5

# compute number of glaciations
glaciations = (icy[0] + np.diff(icy, axis=0).sum(axis=0) + icy[-1]).T/2
footprint = (glaciations > 0)

# set contour levels and colors
levs = np.arange(1, 14)
cmap = iplt.get_cmap('RdBu', len(levs))
colors = cmap(range(len(levs)))

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, glaciations, levels=levs-0.5, colors=colors, extend='max', alpha=0.75)
ax.contour(x, y, glaciations, levels=[9.5], colors='0.75', linewidths=0.25)
ax.contour(x, y, footprint, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ax.add_feature(rivers, zorder=0)
ax.add_feature(lakes, zorder=0)
ax.add_feature(coastline, zorder=0)
ax.add_feature(graticules)

# add colorbar
cb = fig.colorbar(cs, cax, ticks=levs)
cb.set_label(r'number of glaciations')

# save figure
fig.savefig('glaciations')
