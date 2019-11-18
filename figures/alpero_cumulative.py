#!/usr/bin/env python
# Copyright (c) 2016-2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util as ut

# initialize figure
fig, ax, cax, tsax = ut.fi.subplots_cax_ts()

# load aggregated data
# FIXME age coords in preprocessing, open with xarray
with ut.io.open_dataset('../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

    # plot map data
    glaciated = ds.cumu_erosion > 0.0
    ds.cumu_erosion.where(glaciated).plot.contourf(
        ax=ax, alpha=0.75, cmap='Reds', levels=[10**i for i in range(0, 4)],
        cbar_ax=cax, cbar_kwargs=dict(label='total erosion (m)', format='%g'))
    glaciated.plot.contour(ax=ax, colors='k', linewidths=0.5, levels=[0.5])

    # plot time series
    twax = tsax.twinx()
    twax.plot(ds.age/1e3, ds.erosion_rate*1e-9, c='C5')
    twax.set_ylabel('erosion rate ($km\,a^{-1}$)', color='C5')
    twax.set_xlim(120.0, 0.0)
    twax.set_ylim(-0.5, 3.5)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.ne.draw_natural_earth(ax)

# save figure
ut.pl.savefig()
