#!/usr/bin/env python
# coding: utf-8

import util as ut

# initialize figure
fig, ax, cax = ut.fi.subplots_cax()

# add map elements
im = ut.pl.draw_boot_topo(ax)
ut.ne.draw_natural_earth(ax)
ut.na.draw_lgm_outline(ax)
ut.pl.draw_cpu_grid(ax)

# add colorbar
cb = ut.pl.add_colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# save figure
ut.pl.savefig()
