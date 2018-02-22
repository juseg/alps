#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax = ut.pl.subplots_cax(extent='rhlobe')


# Map axes
# --------

# read postprocessed data
f, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'footprint')
a, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'lastflowa')
u, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'lastflowu')
v, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'lastflowv')
u[u.mask] = np.nan  # bug in cartopy streamplot?
v[v.mask] = np.nan  # bug in cartopy streamplot?

# get x and y coordinates
x, y = ut.pl.coords_from_extent(extent, a.shape[1], a.shape[0])

# plot
norm = plt.Normalize(vmin=15.0, vmax=25.0)
ss = ax.streamplot(x, y, u, v, color=a/1e3, cmap='Spectral', norm=norm,
                   density=(12, 8), linewidth=0.5, arrowsize=0.25)
cs = ax.contourf(f*a.mask, extent=extent, levels=[0.5, 1.5], colors='0.5')
cs = ax.contour(f*a.mask, extent=extent, levels=[0.5], colors='k',
                linewidths=0.25, linestyles=[(0, [3, 1])])

# add cartopy vectors
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax, ec='none', fc='w', alpha=0.75)
ut.pl.draw_footprint(ax)

# add colorbar
cb = ut.pl.add_colorbar(ss.lines, cax, extend='both')
cb.set_label(r'age of deglaciation (ka)')

# save figure
ut.pl.savefig()
