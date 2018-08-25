#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(mis=False)


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
                      cmap='Paired', levels=range(21, 28))
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
filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
area = nc.variables['area_glacierized'][:]*1e-9
nc.close()

# print age of max area
#print age[area.argmax()], area.max()

# plot time series
twax = tsax.twinx()
levs = range(21, 28)
cmap = plt.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]
ut.pl.plot_multicolor(age, area, levs[::-1], cols[::-1], ax=twax)
twax.set_ylabel(r'glaciated area ($10^3\,km^2$)',
                color=ut.pl.palette['darkblue'])
twax.set_xlim(29.0, 17.0)
twax.set_ylim(90.0, 170.0)
twax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
