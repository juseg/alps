#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut()


# Map axes
# --------

# read postprocessed data
erosion, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'erosion')

# set levels, colors and hatches
levs = [10**i for i in range(-1, 4)]
cmap = ut.pl.get_cmap('Reds', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot
cs = ax.contourf(erosion, levels=levs, extent=extent, colors=cols, extend='both', alpha=0.75)
ax.contour(erosion.mask, [0.5], extent=extent, colors='k', linewidths=0.5)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax, format='%g')
cb.set_label(r'total erosion (m)')


# Time series
# -----------

# load postprocessed data
age, erosionrate = ut.io.load_postproc_txt(ut.alpcyc_bestrun, 'erosionrate')

# plot time series
twax = tsax.twinx()
twax.plot(age/1e3, erosionrate, c=ut.pl.palette['darkred'])
twax.set_ylabel('erosion rate ($km^3\,a^{-1}$)', color=ut.pl.palette['darkred'])
twax.set_xlim(120.0, 0.0)
twax.set_ylim(-0.5, 3.5)
twax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
