#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# location of time series
xts, yts = 600e3, 5170e3

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()


# Map axes
# --------

# load boot topography
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
its = np.argmin(abs(x-xts))
jts = np.argmin(abs(y-yts))
boot = nc.variables['topg'][its, jts]
nc.close()

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
its = np.argmin(abs(x-xts))
jts = np.argmin(abs(y-yts))
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
dbdt = nc.variables['dbdt'][-1]
topg = nc.variables['topg'][:, jts, its]
nc.close()

# set levels and colors
levs = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
cmap = plt.get_cmap('Greens', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot modern uplift
cs = ax.contourf(x, y, dbdt, levels=levs, colors=cols,
                 extend='both', alpha=0.75)

# add location of time series
ax.plot(xts, yts, 'o', c='w')

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = ut.pl.add_colorbar(cs, cax)
cb.set_label(r'modern uplift rate ($mm\,a^{-1}$)')


# Time series
# -----------

# plot time series
diff = topg - boot
twax = tsax.twinx()
twax.plot(age, diff, c=ut.pl.palette['darkgreen'])
twax.plot(age[-1], diff[-1], 'o', c=ut.pl.palette['darkgreen'], clip_on=False)
twax.set_ylabel('uplift (m)', color=ut.pl.palette['darkgreen'])
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-175.0, 25.0)
twax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
