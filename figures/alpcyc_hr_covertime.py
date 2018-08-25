#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts()


# Map axes
# --------

# read postprocessed data
covertime, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'covertime')

# set contour levels, colors and hatches
levs = [0, 5, 10, 15, 20, 30, 40, 60, 80, 100, 120]
cmap = plt.get_cmap('RdBu', 10)
cols = cmap(range(10))

# plot
cs = ax.contourf(covertime/1e3, levs, extent=extent, colors=cols, alpha=0.75)
ax.contour(covertime > 0.0, [0.5], extent=extent, colors='k', linewidths=0.5)

# add cartopy vectors
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)

# add colorbar
cb = ut.pl.add_colorbar(cs, cax)
cb.set_label(r'ice cover duration (ka)')


# Time series
# -----------

# load time series
filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
area = nc.variables['area_glacierized'][:]*1e-9
nc.close()

# plot time series
c = ut.pl.palette['darkblue']
twax = tsax.twinx()
twax.plot(age, area, c=c)
twax.set_ylabel(r'glaciated area ($10^3\,km^2$)', color=c)
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-25.0, 175.0)
twax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
