#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax, cax = ut.pl.subplots_cax()

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]

# compute footprint
duration = (thk >= 1.0).sum(axis=0).T*0.1
footprint = (duration > 0)
duration[-footprint] = -1

# set contour levels, colors and hatches
levs = [0, 5, 10, 15, 20, 30, 40, 60, 80, 100, 120]
cmap = ut.pl.get_cmap('RdBu', 10)
cols = cmap(range(10))

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, duration, levs, colors=cols, alpha=0.75)
ax.contour(x, y, footprint, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'duration of glaciation (ka)')

# save figure
fig.savefig('duration')
