#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# boot topography
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# add colorbar
cb = fig.colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# add vectors
ut.pl.draw_major_cities(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)

# save figure
fig.savefig('alpcyc_hr_locmap')
