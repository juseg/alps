#!/usr/bin/env python2

# coding: utf-8

import util as ut
import numpy as np

# parameters
xp = 540e3
yd = 5135e3
c = ut.pl.palette['darkblue']

# initialize figure
figw, figh = 170.0, 60.0
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
ax1 = fig.add_axes([2.5/figw, 7.5/figh, 35/figw, 50/figh], projection=ut.pl.utm)
ax2 = fig.add_axes([40.0/figw, 7.5/figh, 120/figw, 50/figh])
ut.pl.add_subfig_label('(a)', ax=ax1)
ut.pl.add_subfig_label('(b)', ax=ax2)


# Map axes
# --------
ax = ax1

# set extent around Rhine catchment
ax.set_extent(ut.pl.regions['rhine'], crs=ax.projection)

# draw boot topography
nc = ut.io.load('input/boot/alps-srtm+gou11simi-1km.nc')
im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# add vectors
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax)

# add profile line
ax.axvline(xp, c=c, ls='--', dashes=(2, 2))
ax.plot(xp, yd, c=c, marker='o')


# Time series
# -----------
ax = ax2

# load extra data
filepath = 'output/0.7.3-craypetsc/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]

# extract space-time slice
i = np.argmin(np.abs(x-xp))
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
thk = nc.variables['thk'][:, i, :]
nc.close()

# plot isotope stages
ut.pl.plot_mis(ax, y=0.925)

# plot envelope
levs = [1.0, 5e3]
cols = [c]
cs = ax.contourf(age, (y-yd)/1e3, thk.T, levels=levs, colors=cols)

# set axes properties
ax.set_xlim(120.0, 0.0)
ax.set_ylim(-60.0, 190.0)
ax.set_xlabel('model age (ka)')
ax.set_ylabel('distance from divide (km)')
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
ax.grid(axis='y')

# save
fig.savefig('alpcyc_hr_profiles')
