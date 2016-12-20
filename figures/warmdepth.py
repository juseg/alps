#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# load and plot boot topo
nc = ut.io.load('input/boot/alps-srtm+gou11simi-1km.nc')
im = nc.imshow('topg', ax, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
boot = nc.variables['topg'][:].T
nc.close()

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]
warm = nc.variables['tempicethk_basal'][:]
temp = nc.variables['temppabase'][:]
nc.close()

# compute mask and warm envelope
mask = (thk < 1.0).prod(axis=0).T
warm = warm.max(axis=0).T
warm = np.ma.masked_where(mask, warm)
#warm = np.ma.masked_less(warm, 1.0)
#surf = boot + warm

# print bounds
#print 'warm ice thickness min %.1f, max %.1f' % (warm.min(), warm.max())

# set contour levels, colors and hatches
levs = [0, 1, 100, 500]
cmap = ut.pl.get_cmap('Reds', len(levs))
cols = cmap(range(len(levs)))
hats = ['//'] + ['']*(len(cols)-1)

# plot
im = ax.contourf(x, y, warm, levs, colors=cols, hatches=hats,
                 extend='max', alpha=0.75)
#ax.contour(x, y, surf, ut.pl.inlevs, colors='0.25', linewidths=0.1)
#ax.contour(x, y, surf, ut.pl.utlevs, colors='0.25', linewidths=0.25)
ax.contour(x, y, warm, [1.0], colors='0.25', linewidths=0.25)
ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.5)

# add cartopy vectors
ut.pl.draw_natural_earth(ax)
#ut.pl.draw_trimlines(ax)

# add colorbar
cb = fig.colorbar(im, cax)
cb.set_label(r'max. basal temp. ice depth (m)')

# save figure
fig.savefig('warmdepth')
