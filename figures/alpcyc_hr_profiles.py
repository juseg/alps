#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp

# parameters
xp = np.array([480e3, 510e3, 540e3, 540e3, 550e3, 510e3, 480e3])
yp = np.array([5170e3, 5180e3, 5190e3, 5230e3, 5260e3, 5290e3, 5290e3])
c = ut.pl.palette['darkblue']

# initialize figure
figw, figh = 170.0, 60.0
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
ax = fig.add_axes([2.5/figw, 7.5/figh, 35/figw, 50/figh], projection=ut.pl.utm)
tsax = fig.add_axes([40.0/figw, 7.5/figh, 120/figw, 50/figh])

# prepare map axes
ax.set_rasterization_zorder(2.5)
ax.set_extent(ut.pl.regions['rhine'], crs=ax.projection)

# add subfigure labels
ut.pl.add_subfig_label('(a)', ax=ax)
ut.pl.add_subfig_label('(b)', ax=tsax)


# Map axes
# --------

# draw boot topography
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# add vectors
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax)

# add profile line
ax.plot(xp, yp, c=c, ls='--', dashes=(2, 2))
ax.plot(xp[0], yp[0], c=c, marker='o')


# Time series
# -----------

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
t = nc.variables['time'][9::10]/(365.0*24*60*60)
h = nc.variables['thk'][9::10]
nc.close()

# extract space-time slice
xi = t[:, None], yp[None, :], xp[None, :]  # coords to sample at
hp = sp.interpolate.interpn((t, y, x), h, xi, method='linear')

# compute distance along profile
dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
dp = np.insert(dp, 0, 0.0)

# plot isotope stages
ut.pl.plot_mis(ax, y=0.925)

# plot envelope
levs = [1.0, 5e3]
cols = [c]
cs = tsax.contourf(-t/1e3, dp/1e3, hp.T, levels=levs, colors=cols)

# set axes properties
tsax.set_xlim(120.0, 0.0)
#tsax.set_ylim(-60.0, 190.0)
tsax.set_xlabel('model age (ka)')
tsax.set_ylabel('distance along profile (km)')
tsax.yaxis.set_label_position("right")
tsax.yaxis.tick_right()
tsax.grid(axis='y')

# save
fig.savefig('alpcyc_hr_profiles')
