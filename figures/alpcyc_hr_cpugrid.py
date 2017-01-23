#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
from matplotlib.collections import LineCollection

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()
w, e, s, n = 150e3, 1050e3, 4820e3, 5420e3

# boot topography
nc = ut.io.load('input/boot/alps-srtm-1km.nc')
im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# add colorbar
cb = fig.colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# add vectors
#ut.pl.draw_natural_earth(ax)
#ut.pl.draw_lgm_outline(ax)
#ut.pl.draw_footprint(ax)

# add grid
x = np.linspace(w, e, 24)
y = np.linspace(s, n, 16)  # 16 until y0087500 then 24)
xx, yy = np.meshgrid(x, y)
vlines = list(np.array([xx, yy]).T)
hlines = list(np.array([xx.T, yy.T]).T)
lines = hlines + vlines
cpugrid = LineCollection(lines, color='k', linewidths=0.25, linestyles=':')
ax.add_collection(cpugrid)

# save figure
fig.savefig('alpcyc_hr_cpugrid')