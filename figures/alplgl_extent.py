#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.fi.subplots_cax(extent='bern')


# Map axes
# --------

# compute stacked extent
stack = -5
offsets = np.arange(-4, 1)
for i, dt in enumerate(offsets):
    filepath = 'output/0.7.3/bern-wc-200m/ramp100acool%04d+alplgl1/y0002000-extra.nc' % (-100*dt)
    nc = ut.io.load(filepath)
    thk = nc.variables['thk'][-1]
    stack = np.where(thk > 1.0, dt, stack)
    if i == 0:
        x = nc.variables['x'][:]
        y = nc.variables['y'][:]
        im = nc.imshow('topg', ax, 0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    nc.close()

# plot
levs = np.append(offsets, 1)-0.5
cs = ax.contourf(x, y, stack.T, levels=levs, cmap='Blues_r', alpha=0.75)
ax.contour(x, y, stack.T, levels=[levs[0]], colors='k',
           linewidths=0.25, linestyles='-')

# add colorbar
cb = ut.pl.add_colorbar(cs, cax, ticks=offsets)
cb.set_label(u'temperature offset (°C)')

# save
ut.pl.savefig()
