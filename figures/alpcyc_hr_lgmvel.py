#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()

# time for plot
a = 24.57
t = -a*1e3


# Map axes
# --------

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)

# plot
im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
im = nc.imshow('velsurf_mag', ax, t, norm=ut.pl.velnorm, cmap='Blues', alpha=0.75)
cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

# close nc file
nc.close()

# add colorbar
cb = ut.pl.add_colorbar(im, cax, extend='both')
cb.set_label(r'surface velocity ($m\,a^{-1}$)')

# add vector elements
ut.pl.draw_natural_earth(ax)
ut.pl.draw_footprint(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_glacier_names(ax)
ut.pl.draw_ice_domes(ax)
ut.pl.draw_major_transfluences(ax)
ut.pl.add_corner_tag('%.2f ka' % a, ax)

# Time series
# -----------

# load time series data
filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# print age of max volume
#print age[vol.argmax()], vol.max()

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
ut.pl.savefig()
