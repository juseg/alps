#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax, cax = util.fig.subplots_cax()

# add map elements
im = util.geo.draw_boot_topo(ax)
util.geo.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)
util.geo.draw_cpu_grid(ax)

# add colorbar
cb = util.com.add_colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# save figure
util.com.savefig()
