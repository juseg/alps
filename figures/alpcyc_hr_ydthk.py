#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(extent='west')

# time for plot
a = 12.5
t = -a*1e3


# Map axes
# --------

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)

# plot
im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
im = nc.imshow('thk', ax, t, vmin=0.0, vmax=3e3, cmap='Blues_r', alpha=0.75)
cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

# close nc file
nc.close()

# add colorbar
cb = ut.pl.add_colorbar(im, cax)
cb.set_label('ice thickness (m)')

# add vector elements
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax)
ut.pl.add_corner_tag('%.2f ka' % a, ax)


# Time series
# -----------

# load time series data
filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]*1e3
nc.close()

# plot time series
tsax=tsax.twinx()
tsax.plot(age, vol, c=ut.pl.palette['darkblue'])
tsax.set_ylabel('ice volume (mm s.l.e.)', color=ut.pl.palette['darkblue'])
tsax.set_xlim(20.0, 0.0)
tsax.set_ylim(-2.5, 17.5)
tsax.locator_params(axis='y', nbins=6)

# add cursor
cursor = tsax.axvline(a, c='k', lw=0.25)

# save figure
ut.pl.savefig()
