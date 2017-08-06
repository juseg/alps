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
fig, grid = ut.pl.subplots_mm(nrows=2, ncols=1, sharex=False, sharey=False,
                              figsize=(figw, figh), projection=ut.pl.utm,
                              left=2.5, right=132.5, bottom=10.0, top=2.5,
                              hspace=2.5, wspace=2.5)

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

    # Map axes
    # --------

    # prepare map axes
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(ut.pl.regions[reg], crs=ax.projection)

    # draw boot topography
    nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
    im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
    nc.close()

    # add vectors
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_lgm_outline(ax)
    ut.pl.draw_footprint(ax)

    # read profile from shapefile
    filename = '../data/native/profile_%s.shp' % reg
    shp = shpreader.Reader(filename)
    geom = shp.geometries().next()
    geom = geom[0]
    xp, yp = np.array(geom).T
    del shp, geom

    # add profile line
    ax.plot(xp, yp, c=c, ls='--', dashes=(2, 2))
    ax.plot(xp[0], yp[0], c=c, marker='o')


    # Time series
    # -----------

    # prepare timeseries axes
    pos = ax.get_position()
    tsrect = [40.0/figw, pos.y0, 120.0/figw, pos.height]
    tsax = fig.add_axes(tsrect)
    ut.pl.plot_mis(tsax, y=0.925)

    # extract space-time slice
    xi = t[:, None], yp[None, :], xp[None, :]  # coords to sample at
    hp = sp.interpolate.interpn((t, y, x), h, xi, method='linear')

    # compute distance along profile
    dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
    dp = np.insert(dp, 0, 0.0)

    # plot envelope
    levs = [1.0, 5e3]
    cols = [c]
    cs = tsax.contourf(-t/1e3, dp/1e3, hp.T, levels=levs, colors=cols)

    # set axes properties
    tsax.set_xlim(120.0, 0.0)
    tsax.set_xlabel('model age (ka)')
    tsax.set_ylabel('%s glacier lenght (km)' % reg.capitalize())
    tsax.xaxis.set_visible(i==len(regions)-1)
    tsax.yaxis.set_label_position("right")
    tsax.yaxis.tick_right()
    tsax.grid(axis='y')

    # add subfigure labels
    ut.pl.add_subfig_label('(%s)' % 'aceg'[i], ax=ax)
    ut.pl.add_subfig_label('(%s)' % 'bdfh'[i], ax=tsax)

# save
fig.savefig('alpcyc_hr_profiles')
