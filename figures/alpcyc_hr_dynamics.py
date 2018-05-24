#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.io.shapereader as shpreader

# parameters
regions = ['rhine', 'rhone', 'ivrea', 'isere']  #, 'inn', 'taglia']
labels = ['Rhine', 'Rhone', 'Dora Baltea', u'Isère']  #, 'Inn', 'Tagliamento']
colors = ['blue', 'green', 'red', 'orange']  #, 'purple', 'brown']
colors = [ut.pl.palette['dark'+hue] for hue in colors]

# initialize figure
fig, ax, cax, scax, hsax, grid = ut.pl.subplots_cax_sc_hs_pf()

# Map axes
# --------

# read postprocessed data
maxthksrf, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthksrf')
maxthkage, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthkage')
maxicethk, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxicethk')
warmbased, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'warmbased')

# set contour levels, colors and hatches
levs = range(21, 28)
cmap = plt.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]

# plot
cs = ax.contourf(warmbased, levels=[0e3, 1e3], extent=extent, hatches=['////'])
cs = ax.contour(warmbased, [1e3], extent=extent, colors='0.25', linewidths=0.25)
im = ax.contourf(maxthkage/1e3, levs, extent=extent, colors=cols, extend='both', alpha=0.75)

# add colorbar
cb = ut.pl.add_colorbar(im, cax)
cb.set_label(r'age of maximum ice surface elevation (ka)')

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_envelope(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_glacier_names(ax)


# Scatter axes
# ------------

# read trimlines data
trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                          dtype=None, delimiter=',', encoding='utf8',
                          names=True)
xt = trimlines['x']
yt = trimlines['y']
zt = trimlines['z']

# convert to UTM 32
xt, yt, zt = ut.pl.utm.transform_points(ut.pl.swiss, xt, yt, zt).T

# load boot topography
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
boot = nc.variables['topg'][:]
nc.close()

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
ht = sp.interpolate.interpn((y, x), maxicethk[::-1], (yt, xt), method='linear')
at = sp.interpolate.interpn((y, x), maxthkage[::-1], (yt, xt), method='linear')/1e3
bt = sp.interpolate.interpn((x, y), boot, (xt, yt), method='linear')

# set contour levels and colors
levs = range(21, 28)
cmap = plt.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]
cmap, norm = mcolors.from_levels_and_colors(levs, cols, extend='both')

# draw scatter plot
sc = scax.scatter(zt, bt+ht, c=at, cmap=cmap, norm=norm, alpha=0.75)
scax.set_xlabel('observed trimline (m)')
scax.set_ylabel('compensated LGM surface (m)', y=0.4)


# Trimlines histogram
# -----------------

# diff between compensated surface elevation and trimlines
dt = bt + ht - zt

# add histogram
step = 100.0
bmin = dt.min() - dt.min() % step
bmax = dt.max() - dt.max() % step + step
bins = np.arange(bmin, bmax+step, step)
hsax.hist(ht, bins=bins, orientation='horizontal', alpha=0.75)
hsax.set_xlabel('frequency')
hsax.set_ylabel('diff. (m)', labelpad=-8, y=1/6.)
hsax.yaxis.set_label_position("right")
hsax.yaxis.tick_right()

# highlight mean thickness
zavg = zt.mean()
davg = dt.mean()
dstd = dt.std()
zz = [zt.min(), zt.max()]
scax.plot(zz, zz+davg, c='0.25')
scax.plot(zz, zz+davg-dstd, c='0.25', dashes=(2, 1), lw=0.5)
scax.plot(zz, zz+davg+dstd, c='0.25', dashes=(2, 1), lw=0.5)
scax.axvline(zavg, c='0.25', dashes=(2, 1), lw=0.5)
scax.axhline(zavg+davg, c='0.25', dashes=(2, 1), lw=0.5)
scax.text(zavg-25.0, (bt+ht).min(), '%.0f m' % zavg, color='0.25',
          rotation=90, rotation_mode='anchor')
scax.text(zz[0], zavg+davg+25.0, '%.0f m' % (zavg+davg), color='0.25')
hsax.axhline(davg, c='0.25')
hsax.axhline(davg-dstd, c='0.25', dashes=(2, 1), lw=0.5)
hsax.axhline(davg+dstd, c='0.25', dashes=(2, 1), lw=0.5)
hsax.text(2.0, davg+25.0, '%.0f m' % davg, color='0.25')

# align axes bounds
hsax.set_ylim(l-zavg for l in scax.get_ylim())


# Glacier profiles
# ----------------

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
    tsax = grid[i]
    label = labels[i]

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

    # extract space-time slice
    xi = t[:, None], yp[None, :], xp[None, :]  # coords to sample at
    hp = sp.interpolate.interpn((t, y, x), h, xi, method='linear')

    # compute distance along profile
    dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
    dp = np.insert(dp, 0, 0.0)

    # plot envelope
    cs = tsax.contourf(-t/1e3, dp/1e3, hp.T, levels=[1.0, 5e3], colors=[c], alpha=0.75)

    # set axes properties
    tsax.set_xlim(120.0, 0.0)
    tsax.set_xlabel('model age (ka)')
    tsax.xaxis.set_visible(i==len(regions)-1)
    tsax.yaxis.set_label_position("right")
    tsax.yaxis.tick_right()
    tsax.grid(axis='y')

# set common y label
grid[2].set_ylabel('glacier length (km)', y=1)

# save figure
ut.pl.savefig()
