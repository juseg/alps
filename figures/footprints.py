#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import numpy as np
import iceplotlib.plot as iplt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp

# projections
ll = ccrs.PlateCarree()
proj = ccrs.UTM(32)

# initialize figure
figw, figh = 135.01, 80.01
fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=proj,
                           left=2.5, right=20.0, bottom=2.5, top=2.5)
cax = fig.add_axes([1-17.5/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])
ax.set_rasterization_zorder(2.5)
    
# draw boot topo
filepath = ('/home/juliens/pism/input/boot/alps-srtm-5km.nc')
nc = iplt.load(filepath)
im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys')
nc.close()

# draw lgm
filename = 'data/lgm_alpen_holefilled.shp'
shp = cshp.Reader(filename)
ax.add_geometries(shp.geometries(), ll, alpha=0.75,
                  edgecolor='#800000', facecolor='none', lw=0.5)

# loop on offsets
offsets = np.arange(9.0, 10.1, 0.1)
footprints = []
for dt in offsets:

    # load data
    filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-5km/'
                'epica3222cool%04d+acyc1/y???????-extra.nc' % (round(dt*100)))
    nc = iplt.load(filepath)
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
