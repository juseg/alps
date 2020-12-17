#!/usr/bin/env python
# Copyright (c) 2017-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import pismx.open
import util

# initialize figure
fig, ax, cax = util.fig.subplots_cax(extent='west')


# Map axes
# --------

# load aggregated data
with pismx.open.dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    age = ds.deglacage
    ext = ds.deglacage.notnull()

    # plot
    ckw = dict(label=r'age of deglaciation (ka)')
    age.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Spectral', levels=range(0, 25, 3))
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.5)

# add cartopy vectors
util.geo.draw_boot_topo(ax)
util.geo.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)

# save figure
util.com.savefig()
