#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]
usurf = nc.variables['usurf'][:]

# compute envelope
mask = (thk < 1.0).prod(axis=0)
envelope = usurf.max(axis=0)
envelope = np.ma.masked_where(mask, envelope)

# print bounds
#print 'LGM envelope min %.1f, max %.1f' % (envelope.min(), envelope.max())

# set contour levels, colors and hatches
levs = range(0, 3001, 1000)
cmap = ut.pl.get_cmap('Blues_r', len(levs))
cols = cmap(range(len(levs)))

# plot
cs = ax.contourf(x, y, envelope, levs, colors=cols, extend='max', alpha=0.75)

# contour levels
ax.contour(x, y, envelope, ut.pl.inlevs, colors='0.25', linewidths=0.1)
ax.contour(x, y, envelope, ut.pl.utlevs, colors='0.25', linewidths=0.25)

# ice margin
ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'maximum ice surface elevation (m)')

# save figure
fig.savefig('alpcyc_hr_envelope')
