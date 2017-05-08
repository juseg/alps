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
c = nc.variables['velbase_mag'][:]
thk = nc.variables['thk'][:]

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
cb = fig.colorbar(cs, cax, format='%.0f')
cb.set_label(r'cumulative basal motion (km)', labelpad=0)


# Time series
# -----------

# compute sliding flux in 1e3 km3/a
dx = x[1] - x[0]
dy = y[1] - y[0]
flux = c.sum(axis=(1, 2))*dx*dy*1e-12

# plot time series
twax = tsax.twinx()
twax.plot(age, flux, c=ut.pl.palette['darkred'])
twax.set_ylabel('sliding flux ($10^3\,km^3\,a^{-1}$)', color=ut.pl.palette['darkred'])
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-2.5, 17.5)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('alpcyc_hr_totalsliding')
