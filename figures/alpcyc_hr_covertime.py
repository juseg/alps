#!/usr/bin/env python
# Copyright (c) 2016-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import hyoga.open
import util

# initialize figure
fig, ax, cax, tsax = util.fig.subplots_cax_ts()


# Map axes
# --------

# load aggregated data
with hyoga.open.dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    ext = ds.covertime > 0.0
    cvt = ds.covertime.where(ext)

    # plot
    ckw = dict(label=r'ice cover duration (ka)')
    cvt.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw, cmap='RdBu',
                      levels=[0, 5, 10, 15, 20, 30, 40, 60, 80, 100, 120])
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.5)

# add cartopy vectors
util.geo.draw_boot_topo(ax)
util.geo.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)


# Time series
# -----------

# load time series
with hyoga.open.dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:

    # plot time series
    twax = tsax.twinx()
    twax.plot(ds.age, ds.area_glacierized/1e9, c='C1')
    twax.set_ylabel(r'glaciated area ($10^3\,km^2$)', color='C1')
    twax.set_xlim(120.0, 0.0)
    twax.set_ylim(-25.0, 175.0)

# save figure
util.com.savefig()
