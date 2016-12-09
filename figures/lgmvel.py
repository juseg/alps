#!/usr/bin/env python2
# coding: utf-8

import util as ut
from matplotlib.colors import LogNorm

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()

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

# close nc file
nc.close()

# add colorbar
cb = fig.colorbar(im, cax, extend='both')
cb.set_label(r'surface velocity ($m\,a^{-1}$)')

# add vector elements
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax)
ut.pl.add_corner_tag('%.1f ka' % a, ax)

# Time series
# -----------

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

# add cursor
cursor = tsax.axvline(a, c='k', lw=0.25)

# save figure
fig.savefig('lgmvel')
