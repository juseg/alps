#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
w, e, s, n = 250, 400, 355, 455  # Zürich
w, e, s, n = 125, 425, 300, 500  # Swiss foreland
w, e, s, n = 000, 901, 000, 601  # Whole domain
x = nc.variables['x'][w:e]
y = nc.variables['y'][s:n]
thk = nc.variables['thk'][:, w:e, s:n]
usurf = nc.variables['usurf'][:, w:e, s:n]

# compute envelope
mask = (thk < 1.0).prod(axis=0).T
envelope = usurf.max(axis=0).T
envelope = np.ma.masked_where(mask, envelope)

# print bounds
#print 'LGM envelope min %.1f, max %.1f' % (envelope.min(), envelope.max())

# set contour levels, colors and hatches
levs = range(0, 5001, 1000)
cmap = ut.pl.get_cmap('Blues_r', len(levs)-1)
cols = cmap(range(len(levs)-1))

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, envelope, levs, colors=cols, alpha=0.75)

# contour levels
ax.contour(x, y, envelope, ut.pl.inlevs, colors='0.25', linewidths=0.1)
ax.contour(x, y, envelope, ut.pl.utlevs, colors='0.25', linewidths=0.25)

# ice margin
ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'maximum ice surface elevation (m)')

# save figure
fig.savefig('envelope')
