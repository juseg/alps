#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax, cax = util.fi.subplots_cax()

# load aggregated data
with util.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    tpg = ds.maxexttpg
    srf = ds.maxextsrf
    fpt = ds.footprint
    ext = ds.maxextthk.notnull()
    age = ds.maxexttpg.age

    # plot
    ckw=dict(label='ice surface elevation (m)')
    tpg.plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                    vmin=0.0, vmax=3e3, zorder=-1)
    fpt.plot.contour(ax=ax, colors=['C7'], levels=[0.5],
                     linewidths=0.5, linestyles=[(0, [3, 1])])
    srf.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Blues_r', levels=range(0, 3001, 1000))
    srf.plot.contour(ax=ax, colors='0.25', levels=util.pl.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors='0.25', levels=util.pl.utlevs, linewidths=0.25)
    ext.plot.contour(ax=ax, levels=[0.5], colors='k', linewidths=0.25)

# add map elements
util.ne.draw_natural_earth(ax)
util.pl.add_corner_tag('%.2f ka' % (age/1e3), ax)

# save figure
util.pl.savefig()
