#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax, cax, tsax = util.fi.subplots_cax_ts()


# Map axes
# --------

# load aggregated data
with util.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    ext = ds.covertime > 0.0
    cvt = ds.covertime.where(ext)/1e3

    # plot
    ckw = dict(label=r'ice cover duration (ka)')
    cvt.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw, cmap='RdBu',
                      levels=[0, 5, 10, 15, 20, 30, 40, 60, 80, 100, 120])
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.5)

# add cartopy vectors
util.pl.draw_boot_topo(ax)
util.geo.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)


# Time series
# -----------

# load time series
with util.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:

    # plot time series
    twax = tsax.twinx()
    twax.plot(ds.age/1e3, ds.area_glacierized/1e9, c='C1')
    twax.set_ylabel(r'glaciated area ($10^3\,km^2$)', color='C1')
    twax.set_xlim(120.0, 0.0)
    twax.set_ylim(-25.0, 175.0)

# save figure
util.pl.savefig()
