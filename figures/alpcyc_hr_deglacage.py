#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax = ut.pl.subplots_cax(extent='west')


# Map axes
# --------

# read postprocessed data
deglacage, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'deglacage')

# set contour levels, colors and hatches
levs = range(0, 25, 2)
cmap = plt.get_cmap('Spectral', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot
cs = ax.contourf(deglacage/1e3, levs, extent=extent, colors=cols, extend='both', alpha=0.75)
ax.contour(deglacage.mask, [0.5], extent=extent, colors='k', linewidths=0.5)

# add cartopy vectors
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax)

# add colorbar
cb = ut.pl.add_colorbar(cs, cax)
cb.set_label(r'age of glaciation (ka)')

# save figure
ut.pl.savefig()
