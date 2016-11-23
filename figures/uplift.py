#!/usr/bin/env python2
# coding: utf-8

import util as ut
import iceplotlib.plot as iplt
from matplotlib.transforms import ScaledTranslation
import cartopy.crs as ccrs

# initialize figure
figw, figh = 135.01, 80.01
fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=ccrs.UTM(32),
                           left=2.5, right=20.0, bottom=2.5, top=2.5)
cax = fig.add_axes([1-17.5/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])
ax.set_rasterization_zorder(2.5)

# load extra data
# FIXME: implement unit conversion (m to mm) in iceplotlib
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
dbdt = nc.variables['dbdt'][-1].T*1e3

# set levels and colors
levs = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
cmap = iplt.get_cmap('Greens', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot modern uplift
im = nc.imshow('topg', ax, -1, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, dbdt, thkth=-1, levels=levs, colors=cols,
                 extend='both', alpha=0.75)

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'modern uplift rate ($mm\,a^{-1}$)')

# close nc file
nc.close()

# save figure
fig.savefig('uplift')
