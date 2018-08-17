#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy.interpolate as sinterp
import cartopy.io.shapereader as shpreader

# parameters
regions = ['rhine', 'rhone', 'ivrea', 'isere', 'inn', 'taglia']
labels = ['Rhine', 'Rhone', 'Dora Baltea', u'Isère', 'Inn', 'Tagliamento']
colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
colors = [ut.pl.palette['dark'+hue] for hue in colors]

# initialize figure
fig, grid, tsgrid = ut.pl.subplots_profiles(regions, labels)

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
t = nc.variables['time'][9::10]/(365.0*24*60*60*1e3)
h = nc.variables['thk'][9::10]
nc.close()

# loop on regions
for i, reg in enumerate(regions):
    c = colors[i]
    ax = grid[i]
    tsax = tsgrid[i]
    label = labels[i]

    # Map axes
    # --------

    # add map elements
    ut.pl.draw_boot_topo(ax)
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_footprint(ax, ec='none', fc='w', alpha=0.75)
    ut.pl.draw_footprint(ax)
    ut.pl.draw_lgm_outline(ax)

    # read profile from shapefile
    filename = '../data/native/profile_%s.shp' % reg
    shp = shpreader.Reader(filename)
    geom = shp.geometries().next()
    geom = geom[0]
    xp, yp = np.array(geom).T
    del shp, geom

    # compute distance along profile
    dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()/1e3
    dp = np.insert(dp, 0, 0.0)

    # spline-interpolate profile
    di = np.arange(0.0, dp[-1], 0.5)
    xp = sinterp.spline(dp, xp, di)
    yp = sinterp.spline(dp, yp, di)
    dp = di

    # add profile line
    ax.plot(xp, yp, c=c, dashes=(2, 1))
    ax.plot(xp[0], yp[0], c=c, marker='o')


    # Time series
    # -----------

    # extract space-time slice
    xi = t[:, None], yp[None, :], xp[None, :]  # coords to sample at
    hp = sinterp.interpn((t, y, x), h, xi, method='linear')

    # plot envelope
    levs = [1.0, 5e3]
    cols = [c]
    cs = tsax.contourf(-t, dp, hp.T, levels=levs, colors=cols, alpha=0.75)

    # set axes properties
    tsax.set_xlim(120.0, 0.0)
    tsax.set_xlabel('model age (ka)')
    tsax.set_ylabel('glacier length (km)')
    tsax.xaxis.set_visible(i==len(regions)-1)
    tsax.yaxis.set_label_position("right")
    tsax.yaxis.tick_right()
    tsax.grid(axis='y')

# save
ut.pl.savefig()
