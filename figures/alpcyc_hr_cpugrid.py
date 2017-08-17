#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# add map elements
im = ut.pl.draw_boot_topo(ax)
#ut.pl.draw_natural_earth(ax)
#ut.pl.draw_lgm_outline(ax)
#ut.pl.draw_footprint(ax)
ut.pl.draw_cpu_grid(ax)

# add colorbar
cb = fig.colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# save figure
fig.savefig('alpcyc_hr_cpugrid')
