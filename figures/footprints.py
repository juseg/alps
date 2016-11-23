#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import cartopy.crs as ccrs

# projections
ll = ccrs.PlateCarree()

# initialize figure
fig, ax, cax = ut.pl.subplots_cax()

# draw boot topo
nc = ut.io.load('input/boot/alps-srtm-5km.nc')
im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys')
nc.close()

# draw lgm
ut.pl.draw_lgm_outline(ax)

# loop on offsets
offsets = np.arange(9.0, 10.1, 0.1)
footprints = []
for dt in offsets:

    # load data
    filepath = ('output/0.7.3/alps-wcnn-5km/'
                'epica3222cool%04d+acyc1/y???????-extra.nc' % (round(dt*100)))
    nc = ut.io.load(filepath)
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    thk = nc.variables['thk'][:]
    nc.close()

    # compute footprint
    duration = (thk >= 1.0).sum(axis=0).T
    footprints.append(duration > 0)

# compute cooling required to cover each grid cell
footprints = np.array(footprints)
isglac = footprints.any(axis=0)
dtglac = np.where(isglac, offsets[footprints.argmax(axis=0)], 99)

# compare to a target area
#isglac = footprints[0]
#lgmarea = 149027868048  # m2
#print isglac.sum()*2000**2 - lgmarea

# plot
#cs = ax.contour(x, y, isglac, linewidths=0.5, colors='k')
cs = ax.contour(x, y, dtglac, offsets, linewidths=0.25, colors='k')
cs = ax.contourf(x, y, dtglac, offsets, cmap='Blues', extend='min', alpha=0.75)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'temperature offset (K)')

# save
fig.savefig('footprints')
