#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut(mis=False)


# Map axes
# --------

# read postprocessed data
maxthksrf, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthksrf')
maxthkage, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthkage')

# set contour levels, colors and hatches
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]

# plot
cs = ax.contourf(maxthkage/1e3, levs, extent=extent, colors=cols, extend='both', alpha=0.75)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_envelope(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_glacier_names(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'age of maximum ice surface elevation (ka)')


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
ut.pl.plot_multicolor(age, area, levs[::-1], cols[::-1], ax=twax)
twax.set_ylabel(r'glaciated area ($10^3\,km^2$)',
                color=ut.pl.palette['darkblue'])
twax.set_xlim(29.0, 17.0)
twax.set_ylim(90.0, 170.0)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('alpcyc_hr_timing')
