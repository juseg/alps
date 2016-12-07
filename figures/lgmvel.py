#!/usr/bin/env python2
# coding: utf-8

import util as ut
from matplotlib.colors import LogNorm

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts()

# time for plot
a = 21.0
t = -a*1e3

# velocity norm
velnorm = LogNorm(1e1, 1e3)


# Map axes
# --------

# contour levels
levs = range(0, 4000, 200)
inlevs = [l for l in levs if l % 1000 != 0]
utlevs = [l for l in levs if l % 1000 == 0]

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)

# plot
im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
im = nc.imshow('velsurf_mag', ax, t, norm=velnorm, cmap='Blues', alpha=0.75)
cs = nc.contour('usurf', ax, t, levels=inlevs, colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=utlevs, colors='0.25', linewidths=0.25)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)
ax.text(0.05, 0.90, '%.1f ka' % a, transform=ax.transAxes)

# close nc file
nc.close()

# add colorbar
cb = fig.colorbar(im, cax)
cb.set_label('ice thickness (m)')

# add vector elements
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax)


# Time series
# -----------

# load temperature signal
nc = ut.io.load('input/dt/epica3222cool0950.nc')
age = -nc.variables['time'][:]/1e3
dt = nc.variables['delta_T'][:]
nc.close()

# plot time series
tsax.plot(age, dt, c='0.25')
tsax.set_xlabel('model age (ka)')
tsax.set_ylabel('temperature offset (K)', color='0.25')
tsax.set_ylim(-12.5, 7.5)

# load time series data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# plot time series
tsax=tsax.twinx()
tsax.plot(age, vol, c=ut.pl.palette['darkblue'])
tsax.set_ylabel('ice volume (m s.l.e.)', color=ut.pl.palette['darkblue'])
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-0.05, 0.35)
tsax.locator_params(axis='y', nbins=6)
tsax.grid(axis='y')

# add cursor
cursor = tsax.axvline(a, c='k', lw=0.25)

# save figure
fig.savefig('lgmvel')
