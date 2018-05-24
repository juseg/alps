#!/usr/bin/env python2
# coding: utf-8

import util as ut
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(dt=False, mis=False)

# time for plot
a = 24.57
t = -a*1e3


# Map axes
# --------

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x, y, vs = nc._extract_xyz('velsurf_mag', t)
x, y, vb = nc._extract_xyz('velbase_mag', t)
w = (3*x[0]-x[1])/2
e = (3*x[-1]-x[-2])/2
n = (3*y[0]-y[1])/2
s = (3*y[-1]-y[-2])/2
vd = vs - vb

# plot
levs = [0.0, 1e0, 1e1, 1e2]
cmap = plt.get_cmap('Blues', len(levs))
cmap.set_under(ut.pl.palette['darkred'])
cols = cmap(range(-1, len(levs)))
im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
im = ax.contourf(x, y, vs-vb, levels=levs, colors=cols, extend='both', alpha=0.75)
cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

# close nc file
nc.close()

# add colorbar
cb = ut.pl.add_colorbar(im, cax, extend='both')
cb.set_label(r'deformation velocity ($m\,a^{-1}$)')

# add vector elements
ut.pl.draw_natural_earth(ax)
ut.pl.draw_footprint(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_glacier_names(ax)
ut.pl.add_corner_tag('%.2f ka' % a, ax)

# Histograms
# ----------

# plot histograms
nbins = [-10**i for i in range(2, -9, -1)] + [0.0]
pbins = [0.0] + [10**i for i in range(-8, 5)]
vd = vd.compressed()
tsax.hist(vd, bins=nbins, color=ut.pl.palette['darkred'], alpha=0.75)
tsax.hist(vd, bins=pbins, color=ut.pl.palette['darkblue'], alpha=0.75)

# set axes properties
tsax.set_xscale('symlog', linthreshx=1e-8, linscalex=1.0)
tsax.set_yscale('log')
tsax.set_xlabel('deformation velocity ($m\,a^{-1}$)')
tsax.set_ylabel('grid cells')
#tsax.locator_params(axis='x', nbins=12)
#tsax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
