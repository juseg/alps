#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# location of time series
xts, yts = 600e3, 5170e3

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()


# Map axes
# --------

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
dbdt = nc.variables['dbdt'][:]*1e3

# set levels and colors
levs = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
cmap = ut.pl.get_cmap('Greens', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot modern uplift
im = nc.imshow('topg', ax, -1, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, dbdt[-1].T, thkth=-1, levels=levs, colors=cols,
                 extend='both', alpha=0.75)

# close nc file
nc.close()

# add location of time series
ax.plot(xts, yts, 'o', c=ut.pl.palette['darkgreen'])

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'modern uplift rate ($mm\,a^{-1}$)')


# Time series
# -----------

# compute central uplift rate
its = np.argmin(abs(x-xts))
jts = np.argmin(abs(y-yts))
dbdt = dbdt[:, its, jts]

# plot time series
twax = tsax.twinx()
twax.plot(age, dbdt, c=ut.pl.palette['darkgreen'])
twax.plot(0.0, dbdt[-1], 'o', c=ut.pl.palette['darkgreen'], clip_on=False)
twax.set_ylabel('uplift rate ($mm\,a^{-1}$)', color=ut.pl.palette['darkgreen'])
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-15.0, 25.0)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('uplift')
