#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import numpy as np
import iceplotlib.plot as iplt
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
w, e, s, n = 250, 400, 355, 455  # Zürich
w, e, s, n = 125, 425, 300, 500  # Swiss foreland
w, e, s, n = 000, 901, 000, 601  # Whole domain
x = nc.variables['x'][w:e]
y = nc.variables['y'][s:n]
time = nc.variables['time'][:]/(365.0*24*60*60)
thk = nc.variables['thk'][:, w:e, s:n]
usurf = nc.variables['usurf'][:, w:e, s:n]

# compute LGM age and envelope
argmax = usurf.argmax(axis=0).T
lgmage = -time[argmax]/1e3
cols, rows = usurf.shape[1:]
envelope = usurf[argmax, np.arange(cols)[None, :], np.arange(rows)[:, None]]

# apply thickness mask
mask = (thk < 1.0).prod(axis=0).T
lgmage = np.ma.masked_where(mask, lgmage)
envelope = np.ma.masked_where(mask, envelope)

# print bounds
#print 'LGM age min %.1f, max %.1f' % (lgmage.min(), lgmage.max())

# set contour levels, colors and hatches
levs = range(21, 28)
cmap = iplt.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, lgmage, levs, colors=cols, extend='both', alpha=0.75)

# contour levels
levs = range(0, 5001, 200)
outer_levs = [l for l in levs if l % 1000 == 0]
inner_levs = [l for l in levs if l % 1000 != 0]
ax.contour(x, y, envelope, inner_levs, colors='0.25', linewidths=0.1)
ax.contour(x, y, envelope, outer_levs, colors='0.25', linewidths=0.25)

# ice margin
ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ax.add_feature(rivers, zorder=0)
ax.add_feature(lakes, zorder=0)
ax.add_feature(coastline, zorder=0)
ax.add_feature(graticules)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'age of maximum ice surface elevation (ka)')

# save figure
fig.savefig('timing')
