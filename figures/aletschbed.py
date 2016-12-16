#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()
ax.set_extent([413e3, 443e3, 5139e3, 5159e3], crs=ax.projection)  # Aletsch

# load boot topography with glaciers
nc = ut.io.load('input/boot/alps-srtm+gou11simi-1km.nc')
surf = nc.variables['topg'][:]
nc.close()

# load boot topography without glaciers
nc = ut.io.load('input/boot/alps-srtmsub+gou11simi-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
base = nc.variables['topg'][:]
nc.close()

# compute difference
diff = surf - base
diff = np.ma.masked_equal(diff, 0.0)

# plot
kwa = dict(edgecolors='w', linewidths=0.25, linestyles=':')
im = ax.pcolormesh(x, y, base.T, vmin=0e3, vmax=3e3, cmap='Greys', **kwa)
im = ax.pcolormesh(x, y, diff.T, vmin=0e2, vmax=5e2, cmap='Blues', **kwa)

# add text labels
w, e, s, n = ax.get_extent()
for (i, j), z in np.ndenumerate(diff):
    xt = x[i] + 0.5e3
    yt = y[j] + 0.5e3
    if w < xt and xt < e and s < yt and yt < n and not diff.mask[i, j]:
        ax.text(xt, yt, '%.0f' % z, ha='center', va='center', color='w')
ax.text(434.5e3, 5140.5e3, 'Fiesch', ha='center', va='center', color='w')

# add colorbar
cb = fig.colorbar(im, cax, extend='both', ticks=[0e2, 5e2])
cb.set_label(r'glacier thickness removed (m)')

# save figure
fig.savefig('aletschbed')
