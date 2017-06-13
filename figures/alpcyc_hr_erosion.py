#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()


# Map axes
# --------

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
thk = nc.variables['thk'][:]
c = nc.variables['velbase_mag'][:]

# compute erosion rate (Herman et al, 2015)
kg = 2.7e-7  # m^{1-l} a^{l-1} 
l = 2.02  # unitless
c = np.ma.masked_where(thk < 1.0, c)
erate = (kg*c**l)
erosion = erate.sum(axis=0)

# set levels, colors and hatches
levs = [10**i for i in range(-2, 3)]
cmap = ut.pl.get_cmap('Reds', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
#norm = ut.pl.iplt.matplotlib.colors.LogNorm(1e-2, 1e5)
#cs = ax.pcolormesh(x, y, erosion, norm=norm, cmap='Reds', alpha=0.75)
cs = ax.contourf(x, y, erosion, levels=levs, colors=cols, extend='both', alpha=0.75)
ax.contour(x, y, erosion, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax, format='%g')
cb.set_label(r'total erosion (m)')


# Time series
# -----------

# compute volumic erosion rate over domain
dx = x[1] - x[0]
dy = y[1] - y[0]
volrate = erate.sum(axis=(1, 2))*dx*dy*1e-9

# plot time series
twax = tsax.twinx()
twax.plot(age, volrate, c=ut.pl.palette['darkred'])
twax.set_ylabel('erosion rate ($km^3\,a^{-1}$)', color=ut.pl.palette['darkred'])
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-1.0, 7.0)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('alpcyc_hr_erosion')
