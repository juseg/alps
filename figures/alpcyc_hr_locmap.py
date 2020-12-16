#!/usr/bin/env python
# Copyright (c) 2016--2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import util


def draw_cpu_grid(ax=None, extent='alps', nx=24, ny=24):
    """Add CPU partition grid."""
    ax = ax or plt.gca()
    w, e, s, n = util.fig.regions[extent]
    x = np.linspace(w, e, 24)
    y = np.linspace(s, n, 24)
    xx, yy = np.meshgrid(x, y)
    vlines = list(np.array([xx, yy]).T)
    hlines = list(np.array([xx.T, yy.T]).T)
    lines = hlines + vlines
    props = dict(color='k', linewidths=0.25, linestyles=':')
    lcoll = mpl.collections.LineCollection(lines, **props)
    ax.add_collection(lcoll)


# initialize figure
fig, ax, cax = util.fig.subplots_cax()

# add map elements
im = util.geo.draw_boot_topo(ax)
util.geo.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)
draw_cpu_grid(ax)

# add colorbar
cb = util.com.add_colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# save figure
util.com.savefig()
