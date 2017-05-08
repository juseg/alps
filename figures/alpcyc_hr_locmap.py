#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import cartopy.io.shapereader as cshp

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# boot topography
nc = ut.io.load('input/boot/alps-srtm+gou11simi-1km.nc')
im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# add colorbar
cb = fig.colorbar(im, cax, extend='both', ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# add vectors
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)

# add cities
offset = 5
shp = cshp.Reader(cshp.natural_earth(resolution='10m',
                                     category='cultural',
                                     name='populated_places_simple'))
for rec in shp.records():
    name = rec.attributes['name'].decode('latin-1')
    rank = rec.attributes['scalerank']
    pop = rec.attributes['pop_max']
    lon = rec.geometry.x
    lat = rec.geometry.y
    if rank <= 5:
        xc, yc = ax.projection.transform_point(lon, lat, src_crs=ut.pl.ll)
        xloc = 'r'  #('l' if xc < center[0] else 'r')
        yloc = 'u'  #('l' if yc < center[1] else 'u')
        dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*offset
        dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*offset
        ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
        va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
        ax.plot(xc, yc, 'ko')
        ax.annotate(name, xy=(xc, yc), xytext=(dx, dy),
                    textcoords='offset points', ha=ha, va=va, clip_on=True)

# save figure
fig.savefig('alpcyc_hr_locmap')
