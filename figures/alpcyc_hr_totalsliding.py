#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()


# Map axes
# --------

# read postprocessed data
totalslip, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'totalslip')

# set levels, colors and hatches
levs = [10**(0.5*i) for i in range(4, 11)]
cmap = ut.pl.get_cmap('Reds', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot
cs = ax.contourf(totalslip/1e3, levels=levs, extent=extent, colors=cols, extend='both', alpha=0.75)
ax.contour(totalslip.mask, [0.5], extent=extent, colors='k', linewidths=0.5)

# add cartopy vectors
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax, format='%.0f')
cb.set_label(r'cumulative basal motion (km)', labelpad=0)


# Time series
# -----------

# load postprocessed data
age, slidingflux = ut.io.load_postproc_txt(ut.alpcyc_bestrun, 'slidingflux')

# plot time series
twax = tsax.twinx()
twax.plot(age/1e3, slidingflux/1e3, c=ut.pl.palette['darkred'])
twax.set_ylabel('sliding flux ($10^3\,km^3\,a^{-1}$)', color=ut.pl.palette['darkred'])
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-1.0, 7.0)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('alpcyc_hr_totalsliding')
