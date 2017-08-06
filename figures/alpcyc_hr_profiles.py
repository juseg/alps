#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp
import cartopy.io.shapereader as shpreader

# parameters
regions = ['rhine', 'ivrea']
colors = [ut.pl.palette[c] for c in ['darkblue', 'darkred']]

# initialize figure
figw, figh = 170.0, 115.0
ax_bottoms = [(7.5+i*52.5)/figh for i in range(2)[::-1]]
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
grid = [fig.add_axes([2.5/figw, b, 35.0/figw, 50.0/figh], projection=ut.pl.utm)
        for b in ax_bottoms]
tsgrid = [fig.add_axes([40.0/figw, b, 120.0/figw, 50.0/figh])
          for b in ax_bottoms]

# prepare map axes
for i, ax in enumerate(grid):
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(ut.pl.regions[regions[i]], crs=ax.projection)

# add subfigure labels
for i, ax in enumerate(grid):
    ut.pl.add_subfig_label('(%s)' % 'abcdefgh'[i], ax=ax)

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
t = nc.variables['time'][9::10]/(365.0*24*60*60)
h = nc.variables['thk'][9::10]
nc.close()

# loop on regions
for i, reg in enumerate(regions):
    c = colors[i]
    ax = grid[i]
    tsax = tsgrid[i]

    # Map axes
    # --------

    # draw boot topography
    nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
    im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
    nc.close()

    # add vectors
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_lgm_outline(ax)
    ut.pl.draw_footprint(ax)

    # read profile from shapefile
    filename = '../data/native/profile_%s.shp' % regions[i]
    shp = shpreader.Reader(filename)
    geom = shp.geometries().next()
    geom = geom[0]
    xp, yp = np.array(geom).T
    del shp

    # add profile line
    ax.plot(xp, yp, c=c, ls='--', dashes=(2, 2))
    ax.plot(xp[0], yp[0], c=c, marker='o')


    # Time series
    # -----------

    # extract space-time slice
    xi = t[:, None], yp[None, :], xp[None, :]  # coords to sample at
    hp = sp.interpolate.interpn((t, y, x), h, xi, method='linear')

    # compute distance along profile
    dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
    dp = np.insert(dp, 0, 0.0)

    # plot isotope stages
    ut.pl.plot_mis(tsax, y=0.925)

    # plot envelope
    levs = [1.0, 5e3]
    cols = [c]
    cs = tsax.contourf(-t/1e3, dp/1e3, hp.T, levels=levs, colors=cols)

    # set axes properties
    tsax.set_xlim(120.0, 0.0)
    tsax.set_xlabel('model age (ka)')
    tsax.set_ylabel('distance along profile (km)')
    tsax.yaxis.set_label_position("right")
    tsax.yaxis.tick_right()
    tsax.grid(axis='y')

# save
fig.savefig('alpcyc_hr_profiles')
