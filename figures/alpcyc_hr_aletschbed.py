#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax(extent='aletsch')

# load boot topographies
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
base = nc.variables['topg'][:]
diff = nc.variables['thk'][:]
nc.close()

# mask zero thickness
diff = np.ma.masked_equal(diff, 0.0)

# plot
kwa = dict(edgecolors='w', linewidths=0.25, linestyles=':')
im = ax.pcolormesh(x, y, base.T, vmin=0e3, vmax=3e3, cmap='Greys', **kwa)
im = ax.pcolormesh(x, y, diff.T, vmin=0e2, vmax=5e2, cmap='Blues', alpha=0.75, **kwa)

# add text labels
w, e, s, n = ax.get_extent()
for (i, j), z in np.ndenumerate(diff):
    xt = x[i] + 0.5e3
    yt = y[j] + 0.5e3
    if w < xt and xt < e and s < yt and yt < n and not diff.mask[i, j]:
        ax.text(xt, yt, '%.0f' % z, ha='center', va='center', color='w')
ax.text(434.5e3, 5140.5e3, 'Fiesch', ha='center', va='center', color='k')

# add colorbar
cb = ut.pl.add_colorbar(im, cax, extend='both', ticks=[0e2, 5e2])
cb.set_label(r'glacier thickness removed (m)', labelpad=0)

# save figure
ut.pl.savefig()
