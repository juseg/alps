#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# load and plot boot topo
nc = ut.io.load('input/boot/alps-srtm+gou11simi-1km.nc')
im = nc.imshow('topg', ax, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
boot = nc.variables['topg'][:].T
nc.close()

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]
temp = nc.variables['temppabase'][:]
nc.close()

# compute duration of warm-based coved
warm = temp > -1e-9
warm = np.ma.masked_where(thk < 1.0, warm)
warm = warm.sum(axis=0)*0.1

# set levels, colors and hatches
levs = [0, 1, 20, 40, 60, 80, 100, 120]
cmap = ut.pl.get_cmap('Reds', len(levs)-1)
cols = cmap(range(len(levs)-1))
hats = ['//'] + ['']*(len(cols)-1)

# plot
im = ax.contourf(x, y, warm.T, levs, colors=cols, hatches=hats, alpha=0.75)
ax.contour(x, y, warm.T, [1.0], colors='0.25', linewidths=0.25)
ax.contour(x, y, warm.mask.T, [0.5], colors='k', linewidths=0.5)

# add vectors
ut.pl.draw_natural_earth(ax)
#ut.pl.draw_trimlines(ax)

# add colorbar
cb = fig.colorbar(im, cax)
cb.set_label('duration of warm ice cover (ka)')

# save figure
fig.savefig('alpcyc_hr_warmtime')