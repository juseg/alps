#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# set contour levels, colors and hatches
levs = range(0, 3001, 1000)
cmap = ut.pl.get_cmap('Blues_r', len(levs))
cols = cmap(range(len(levs)))

# plot
cs = ut.pl.draw_envelope(ax, levs, cols)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'maximum thickness surface elevation (m)')

# save figure
ut.pl.savefig()
