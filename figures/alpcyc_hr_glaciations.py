#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]

# compute footprint
icy = (thk >= 1.0)

# filter out short glaciations
#icysum = icy.cumsum(axis=0)
#icy = (icysum[5:] - icysum[:-5])/5

# compute number of glaciations
glaciations = (icy[0] + np.diff(icy, axis=0).sum(axis=0) + icy[-1])/2
footprint = (glaciations > 0)

# set contour levels and colors
levs = np.arange(1, 14)
cmap = ut.pl.get_cmap('RdBu', len(levs))
colors = cmap(range(len(levs)))

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, glaciations, levels=levs-0.5, colors=colors, extend='max', alpha=0.75)
ax.contour(x, y, glaciations, levels=[9.5], colors='0.75', linewidths=0.25)
ax.contour(x, y, footprint, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax, ticks=levs)
cb.set_label(r'number of glaciations')

# save figure
fig.savefig('alpcyc_hr_glaciations')
