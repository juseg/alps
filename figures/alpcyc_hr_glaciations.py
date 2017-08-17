#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# read postprocessed data
nadvances, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'nadvances')

# set contour levels and colors
levs = np.arange(1, 14)
cmap = ut.pl.get_cmap('RdBu', len(levs))
cols = cmap(range(len(levs)))

# plot
cs = ax.contourf(nadvances, levs-0.5, extent=extent, colors=cols, extend='max', alpha=0.75)
ax.contour(nadvances, [9.5], extent=extent, colors='0.75', linewidths=0.25)
ax.contour(nadvances, [0.5], extent=extent, colors='k', linewidths=0.5)

# add cartopy vectors
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax, ticks=levs)
cb.set_label(r'number of glaciations')

# save figure
fig.savefig('alpcyc_hr_glaciations')
