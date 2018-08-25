#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts()


# Map axes
# --------

# load aggregated data
with ut.io.load_postproc('alpcyc.1km.epic.pp.agg.nc') as ds:
    ext = ds.covertime > 0.0
    cvt = ds.covertime.where(ext)/1e3

    # plot
    ckw = dict(label=r'ice cover duration (ka)')
    cvt.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw, cmap='RdBu',
                      levels=[0, 5, 10, 15, 20, 30, 40, 60, 80, 100, 120])
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.5)

# add cartopy vectors
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)


# Time series
# -----------

# load time series
filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
area = nc.variables['area_glacierized'][:]*1e-9
nc.close()

# plot time series
c = 'C1'
twax = tsax.twinx()
twax.plot(age, area, c=c)
twax.set_ylabel(r'glaciated area ($10^3\,km^2$)', color=c)
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-25.0, 175.0)
twax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
