#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax, cax = util.fi.subplots_cax()

# add map elements
im = util.pl.draw_boot_topo(ax)
util.ne.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)
util.pl.draw_cpu_grid(ax)

# add colorbar
cb = util.pl.add_colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# save figure
util.pl.savefig()
