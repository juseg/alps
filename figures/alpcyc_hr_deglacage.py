#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax, cax = util.fig.subplots_cax(extent='west')


# Map axes
# --------

# load aggregated data
with util.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    age = ds.deglacage/1e3
    ext = ds.deglacage.notnull()

    # plot
    ckw = dict(label=r'age of deglaciation (ka)')
    age.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Spectral', levels=range(0, 25, 3))
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.5)

# add cartopy vectors
util.pl.draw_boot_topo(ax)
util.geo.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)

# save figure
util.pl.savefig()
