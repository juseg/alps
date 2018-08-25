#!/usr/bin/env python2
# coding: utf-8

import util as ut
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(mis=False)

# age levels and colors
levs = range(21, 28)
cols = plt.get_cmap('Paired').colors[:len(levs)+1]

# Map axes
# --------

# load aggregated data
with ut.io.load_postproc('alpcyc.1km.epic.pp.agg.nc') as ds:
    age = ds.maxthkage/1e3
    srf = ds.maxthksrf
    ext = ds.maxthksrf.notnull()

    # plot
    ckw = dict(label=r'age of maximum ice thickness (ka)')
    age.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      colors=cols, levels=levs)
    srf.plot.contour(ax=ax, colors='0.25', levels=ut.pl.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors='0.25', levels=ut.pl.utlevs,
                     linewidths=0.25)
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.25)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_glacier_names(ax)


# Time series
# -----------

# load time series
with ut.io.load_postproc('alpcyc.1km.epic.pp.ts.10a.nc') as ds:

    # plot time series
    twax = tsax.twinx()
    bnds = [0] + levs + [120]
    for i, c in enumerate(cols):
        area = ds.area_glacierized[(bnds[i]<=ds.age)*(ds.age<=bnds[i+1])]/1e9
        area.plot(color=c, lw=2.0)

    twax.set_ylabel(r'glaciated area ($10^3\,km^2$)', color='C1')
    twax.set_xlim(29.0, 17.0)
    twax.set_ylim(90.0, 170.0)

# save figure
ut.pl.savefig()
