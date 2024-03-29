#!/usr/bin/env python
# coding: utf-8

import hyoga.open
import util

# initialize figure
fig, ax, cax = util.fig.subplots_cax()

# load aggregated data
with hyoga.open.dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    thk = ds.maxextthk
    tpg = ds.maxexttpg
    srf = ds.maxextsrf
    fpt = ds.footprint
    ext = ds.maxextthk.notnull()
    age = ds.maxexttpg.age

    # plot
    ckw=dict(label='ice thickness (m)')
    tpg.plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                    vmin=0.0, vmax=3e3, zorder=-1)
    fpt.plot.contour(ax=ax, colors=['C7'], levels=[0.5],
                     linewidths=0.5, linestyles=[(0, [3, 1])])
    thk.plot.imshow(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                    cmap='Blues_r', vmin=0.0, vmax=3e3)
    srf.plot.contour(ax=ax, colors='0.25', levels=util.com.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors='0.25', levels=util.com.utlevs, linewidths=0.25)
    ext.plot.contour(ax=ax, levels=[0.5], colors='k', linewidths=0.25)

# add vector elements
util.geo.draw_natural_earth(ax)
util.com.add_corner_tag('%.2f ka' % (age/1e3), ax=ax)

# save figure
util.com.savefig()
