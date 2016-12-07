#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax, cax = ut.pl.subplots_cax_inset()

# load extra data
# FIXME: implement unit conversion (m to mm) in iceplotlib
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
dbdt = nc.variables['dbdt'][-1].T*1e3

# set levels and colors
levs = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
cmap = ut.pl.get_cmap('Greens', len(levs)+1)
cols = cmap(range(len(levs)+1))

# plot modern uplift
im = nc.imshow('topg', ax, -1, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, dbdt, thkth=-1, levels=levs, colors=cols,
                 extend='both', alpha=0.75)

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'modern uplift rate ($mm\,a^{-1}$)')

# close nc file
nc.close()

# save figure
fig.savefig('uplift')
