#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# initialize figure
fig, grid = ut.pl.subplots_inputs()

# add map elements
for i, ax in enumerate(grid.flat):
    im = ut.pl.draw_boot_topo(ax)
    ut.pl.draw_natural_earth(ax)

# add boot topo colorbar
ticks = range(0, 3001, 1000)
ax = grid[0, 1]
cb = ut.pl.add_colorbar(im, ax.cax, extend='max', ticks=ticks)
ax.cax.set_yticklabels(['%.0f' % (t*1e-3) for t in ticks])
cb.set_label(r'Basal topography (km)')

# add LGM outline on these axes
ut.pl.draw_lgm_outline(ax)

# Boot file
# ---------

# open boot file
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')

# contour levels and colors
levs = range(60, 91, 5)
cmap = plt.get_cmap('PuOr_r', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot geothermal flux
ax = grid[0, 0]
cs = nc.contourf('bheatflx', ax, levels=levs, colors=cols, thkth=-1,
                 extend='both', alpha=0.75)

# add colorbar
cb = ut.pl.add_colorbar(cs, ax.cax, extend='both', ticks=levs[::2])
cb.set_label(r'Geothermal flux ($mW\,m^{-2}$)')

# add scale
w, e, s, n = ax.get_extent()
ax.plot([e-260e3, e-60e3], [s+60e3]*2, 'w|-')
ax.text(e-160e3, s+90e3, r'100$\,$km', color='w', ha='center', fontweight='bold')

# plot boot ice thickness
ax = grid[0, 2]
ax.set_extent(ut.pl.regions['bern'], crs=ax.projection)
im = nc.imshow('thk', ax, vmin=0e2, vmax=6e2, cmap='Blues', alpha=0.75)

# add colorbar
cb = ut.pl.add_colorbar(im, ax.cax, extend='max', ticks=range(0, 601, 200))
cb.set_label(r'Modern ice thickness (m)')

# close boot file
nc.close()

# add scale
w, e, s, n = ax.get_extent()
ax.plot([e-25e3, e-5e3], [s+5e3]*2, 'w|-')
ax.text(e-15e3, s+7.5e3, r'20$\,$km', color='w', ha='center', fontweight='bold')


# Standard deviation
# ------------------

# load standard deviation file
# FIXME: add unit conversion to iceplotlib
nc = ut.io.load('input/sd/alps-erai-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
sd = nc.variables['air_temp_sd'][:]
nc.close()

# contour levels and colors
levs = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
cmap = plt.get_cmap('Purples', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot standard deviation
for i in range(2):
    ax = grid[i+1, 0]
    cs = ax.contourf(x, y, sd[6*i].T, levs, colors=cols, extend='both', alpha=0.75)
    ut.pl.add_corner_tag(['Jan.', 'July'][i], ax=ax, va='bottom')

# add colorbar
cb = ut.pl.add_colorbar(cs, ax.cax, ticks=levs[::2])
cb.set_label(u'PDD SD (°C)')


# Temperature and precipitation
# -----------------------------

# load atm file
# FIXME: add unit conversion to iceplotlib
nc = ut.io.load('input/atm/alps-wcnn-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
temp = nc.variables['air_temp'][:]
prec = nc.variables['precipitation'][:]
nc.close()

# contour levels and colors
levs = range(-10, 21, 5)
cmap = plt.get_cmap('RdBu_r', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot January and July temperature
ax = grid.flat[2]
for i in range(2):
    ax = grid[i+1, 1]
    cs = ax.contourf(x, y, temp[6*i].T-273.15, levs, colors=cols, extend='both', alpha=0.75)
    ut.pl.add_corner_tag(['Jan.', 'July'][i], ax=ax, va='bottom')

# add colorbar
cb = ut.pl.add_colorbar(cs, ax.cax, ticks=levs[::2])
cb.set_label(u'Air temperature (°C)')

# contour levels and colors
levs = range(50, 251, 50)
cmap = plt.get_cmap('Greens', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot January and July precipitation
for i in range(2):
    ax = grid[i+1, 2]
    cs = ax.contourf(x, y, prec[6*i].T*910.0/12, levs, colors=cols, extend='both', alpha=0.75)
    ut.pl.add_corner_tag(['Jan.', 'July'][i], ax=ax, va='bottom')

# add colorbar
cb = ut.pl.add_colorbar(cs, ax.cax, ticks=levs[1::2])
cb.set_label(r'Monthly precipitation (mm)')

# save
ut.pl.savefig()
