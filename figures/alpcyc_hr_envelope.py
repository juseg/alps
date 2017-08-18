#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# read postprocessed data
maxthksrf, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxicesrf')

# set contour levels, colors and hatches
levs = range(0, 3001, 1000)
cmap = ut.pl.get_cmap('Blues_r', len(levs))
cols = cmap(range(len(levs)))

# plot
cs = ax.contourf(maxthksrf, levs, extent=extent, colors=cols, extend='max', alpha=0.75)
ax.contour(maxthksrf, ut.pl.inlevs, extent=extent, colors='0.25', linewidths=0.1)
ax.contour(maxthksrf, ut.pl.utlevs, extent=extent, colors='0.25', linewidths=0.25)
ax.contour(maxthksrf.mask, [0.5], extent=extent, colors='k', linewidths=0.5)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'maximum ice surface elevation (m)')

# save figure
fig.savefig('alpcyc_hr_envelope')
