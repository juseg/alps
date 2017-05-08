#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()


# Map axes
# --------

# load extra data
filepath = 'output/0.7.3-craypetsc/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
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
ut.pl.draw_lgm_outline(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'duration of glaciation (ka)')

# Time series
# -----------

# compute glaciated areas in 1e3 km2
dx = x[1] - x[0]
dy = y[1] - y[0]
area = (thk >= 1.0).sum(axis=(1, 2))*dx*dy*1e-9

# plot time series
c = ut.pl.palette['darkblue']
twax = tsax.twinx()
twax.plot(age, area, c=c)
twax.set_ylabel(r'glaciated area ($10^3\,km^2$)', color=c)
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-25.0, 175.0)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('alpcyc_hr_duration')
