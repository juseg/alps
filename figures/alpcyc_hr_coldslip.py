#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(dt=False, mis=False)
tsax.set_rasterization_zorder(2.5)

# time for plot
a = 24.57
t = -a*1e3


# Map axes
# --------

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x, y, temp = nc._extract_xyz('temppabase', t)
x, y, slip = nc._extract_xyz('velbase_mag', t)

# identify problematic areas
cold = (temp < -1e-3)
coldslip = np.ma.masked_where(1-cold, slip)
warmslip = np.ma.masked_where(cold, slip)

# set contour levels, colors and hatches
levs = [1e-1, 1e0, 1e1]
cmap = plt.get_cmap('Blues', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot
im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
im = nc.imshow('velbase_mag', ax, t, norm=ut.pl.velnorm, cmap='Reds', alpha=0.75)
im = ax.contourf(x, y, coldslip, levels=levs, colors=cols, extend='both', alpha=0.75)
cs = nc.contour('temppabase', ax, t, levels=[-1e-3], colors='k',
                linewidths=0.25, linestyles=['-'], zorder=0)
cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

# close nc file
nc.close()

# add colorbar
cb = ut.pl.add_colorbar(im, cax, extend='both')
cb.set_label('cold-based sliding ($m\,a^{-1}$)')

# add vector elements
ut.pl.draw_natural_earth(ax)
ut.pl.add_corner_tag('%.2f ka' % a, ax)


# Time series
# -----------

# plot scatter
tsax.set_yscale('log')
tsax.set_xscale('symlog', linthreshx=1e-12)
tsax.scatter(temp, coldslip, marker='.', c=ut.pl.palette['darkblue'], alpha=0.1)
tsax.scatter(temp, warmslip, marker='.', c=ut.pl.palette['darkred'], alpha=0.1)
tsax.set_xlabel('basal temperature below freezing (K)')
tsax.set_ylabel('basal velocity ($m\,a^{-1}$)')

# save figure
ut.pl.savefig()
