#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax, cax1, cax2, tsax = util.fig.subplots_cax_ts_sgm()

# time for plot
a = 24.559
t = -a*1e3


# Map axes
# --------

# load extra data
runname = 'output/1.0/alps-wcnn-500m/epica3222cool1220+alpcyc4+pp/'
filepath = runname + 'y0095460-extra.nc'
nc = util.io.load(filepath)

# more contour levels than other plots
topolevs = range(0, 5000, 100)
inlevs = [l for l in topolevs if l % 1000 != 0]
utlevs = [l for l in topolevs if l % 1000 == 0]

# plot
im1 = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
#im = nc.shading('topg', ax, t, zorder=-1)
im2 = nc.imshow('velsurf_mag', ax, t, norm=util.pl.velnorm, cmap='Blues', alpha=0.75)
cs = nc.contour('usurf', ax, t, levels=inlevs, colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=utlevs, colors='0.25', linewidths=0.25)
cs.clabel(color='0.25', fmt='%d', fontsize=4)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

## frozen bed areas
#cs = nc.contourf('temppabase', ax, t, levels=[-50.0, -1e-6],
#                 cmap=None, colors='none', hatches=['////'], zorder=0)
#cs = nc.contour('temppabase', ax, t, levels=[-50.0, -1e-6],
#                colors='k', linewidths=0.25, linestyles=['-'], zorder=0)

# close nc file
nc.close()

# add colorbars
cb = util.pl.add_colorbar(im1, cax1, extend='both')
cb.set_label(r'bedrock topography (m)')
cb = util.pl.add_colorbar(im2, cax2, extend='both')
cb.set_label(r'surface velocity ($m\,a^{-1}$)')

# add vector polygons
util.geo.draw_natural_earth(ax)
util.geo.draw_footprint(ax)
util.geo.draw_lgm_outline(ax)
util.flo.draw_ice_divides(ax)
util.flo.draw_water_divides(ax)

# add vector points and labels
util.geo.draw_major_cities(ax)
util.flo.draw_glacier_names(ax)
util.flo.draw_cross_divides(ax)
util.flo.draw_transfluences(ax)
util.flo.draw_ice_domes(ax)
util.pl.add_corner_tag('%.2f ka' % a, ax)


# Time series
# -----------

# load time series data
filepath = util.alpcyc_bestrun + 'y???????-ts.nc'
nc = util.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# print age of max volume
#print age[vol.argmax()], vol.max()

# plot time series
tsax=tsax.twinx()
tsax.plot(age, vol, c='C1')
tsax.set_ylabel('ice volume (m s.l.e.)', color='C1')
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-0.05, 0.35)
tsax.locator_params(axis='y', nbins=6)

# add cursor
cursor = tsax.axvline(a, c='k', lw=0.25)

# save figure
util.pl.savefig()
