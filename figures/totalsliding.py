#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# load extra data
# FIXME: implement regional data extraction in iceplotlib
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
w, e, s, n = 125, 425, 300, 500  # Swiss foreland
w, e, s, n = 000, 901, 000, 601  # Whole domain
x = nc.variables['x'][w:e]
y = nc.variables['y'][s:n]
c = nc.variables['velbase_mag'][:, w:e, s:n]
thk = nc.variables['thk'][:, w:e, s:n]

# compute total basal sliding
totalsliding = np.ma.array(c, mask=(thk < 1.0)).sum(axis=0).T
footprint = totalsliding.mask

# set levels, colors and hatches
levs = [10**(0.5*i) for i in range(4, 11)]
cmap = ut.pl.get_cmap('Reds', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, totalsliding, levels=levs, colors=cols, extend='both', alpha=0.75)
ax.contour(x, y, footprint, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'cumulative basal motion (km)', labelpad=0)

# save figure
fig.savefig('totalsliding')
