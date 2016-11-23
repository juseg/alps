#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import iceplotlib.plot as iplt
from mayavi import mlab

# subsampling stride
stride = 1

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
w, e, s, n = 250, 400, 355, 455  # Zürich
w, e, s, n = 125, 425, 300, 500  # Swiss foreland
w, e, s, n = 000, 901, 000, 601  # Whole domain
x = nc.variables['x'][w:e:stride]
y = nc.variables['y'][s:n:stride]
thk = nc.variables['thk'][-1, w:e:stride, s:n:stride]
topg = nc.variables['topg'][-1, w:e:stride, s:n:stride]
usurf = nc.variables['usurf'][-1, w:e:stride, s:n:stride]
nc.close()
mask = thk<1.0

# initialize figure
mlab.figure(size=(1350, 800))

# plot basal and surface topographies
exag = 3.0
surf = mlab.surf(x, y, topg, vmin=0e3, vmax=3e3, colormap='Greys',
                 warp_scale=exag)
surf = mlab.surf(x, y, usurf, vmin=0e3, vmax=3e3, colormap='Blues',
                 mask=mask, opacity=0.75, warp_scale=exag)
surf.module_manager.scalar_lut_manager.reverse_lut = True

# plot surface elevation contour
levs = range(0, 4000, 200)
inner_levs = [l for l in levs if l % 1000 != 0]
outer_levs = [l for l in levs if l % 1000 == 0]
#surf = mlab.contour_surf(x, y, usurf, contours=inner_levs,
#                         color=(0, 0, 0), line_width=0.5, warp_scale=exag)
surf = mlab.contour_surf(x, y, usurf, contours=outer_levs,
                         color=(0, 0, 0), line_width=1.0, warp_scale=exag)

# show or save
mlab.show()
#mlab.savefig('mayavitest.jpg')
