#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp
import cartopy.io.shapereader as shpreader

# parameters
regions = ['rhine', 'rhone', 'ivrea', 'isere', 'inn', 'taglia']
labels = ['Rhine', 'Rhone', 'Ivrea', u'Isère', 'Inn', 'Tagliamento']
colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
colors = [ut.pl.palette['dark'+hue] for hue in colors]

# initialize figure
figw, figh = 170.0, 175.0
fig, grid = ut.pl.subplots_mm(nrows=6, ncols=1, sharex=False, sharey=False,
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
    label = labels[i]

    # Map axes
    # --------

    # prepare map axes
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(ut.pl.regions[reg], crs=ax.projection)

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

    # add profile line
    ax.plot(xp, yp, c=c, dashes=(2, 1))
    ax.plot(xp[0], yp[0], c=c, marker='o')


    # Time series
    # -----------

    # prepare timeseries axes
    pos = ax.get_position()
    tsrect = [40.0/figw, pos.y0, 120.0/figw, pos.height]
    tsax = fig.add_axes(tsrect)
    ut.pl.plot_mis(tsax, y=(0.15 if i==len(regions)-1 else None))

    # extract space-time slice
    xi = t[:, None], yp[None, :], xp[None, :]  # coords to sample at
    hp = sp.interpolate.interpn((t, y, x), h, xi, method='linear')

    # compute distance along profile
    dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
    dp = np.insert(dp, 0, 0.0)

    # plot envelope
    levs = [1.0, 5e3]
    cols = [c]
    cs = tsax.contourf(-t/1e3, dp/1e3, hp.T, levels=levs, colors=cols, alpha=0.75)

    # set axes properties
    tsax.set_xlim(120.0, 0.0)
    tsax.set_xlabel('model age (ka)')
    tsax.set_ylabel('glacier length (km)')
    tsax.xaxis.set_visible(i==len(regions)-1)
    tsax.yaxis.set_label_position("right")
    tsax.yaxis.tick_right()
    tsax.grid(axis='y')

    # add subfigure labels
    ut.pl.add_subfig_label('(%s)' % 'acegik'[i], ax=ax)
    ut.pl.add_subfig_label('(%s) ' % 'bdfhjl'[i] + label, ax=tsax)

# save
fig.savefig('alpcyc_hr_profiles')
