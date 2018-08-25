#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

fig, ax, cax, scax, hsax = ut.pl.subplots_trimlines()


# Input data
# ----------

# read trimlines data
trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                          dtype=None, delimiter=',', encoding='utf8',
                          names=True)
xt = trimlines['x']
yt = trimlines['y']
zt = trimlines['z']

# convert to UTM 32
xt, yt, zt = ut.pl.utm.transform_points(ut.pl.swiss, xt, yt, zt).T

# load aggregated data
# FIXME use xarray interpolation methods
with ut.io.load_postproc('alpcyc.1km.epic.pp.agg.nc') as ds:
    maxthkthk = ds.maxthkthk.data
    maxthkage = ds.maxthkage.data

# load boot topography
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
boot = nc.variables['topg'][:]
nc.close()

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
ht = sp.interpolate.interpn((y, x), maxthkthk, (yt, xt), method='linear')
at = sp.interpolate.interpn((y, x), maxthkage, (yt, xt), method='linear')/1e3
bt = sp.interpolate.interpn((x, y), boot, (xt, yt), method='linear')


# Scatter axes
# ------------

# set contour levels and colors
levs = range(21, 28)
cmap = plt.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]
cmap, norm = mcolors.from_levels_and_colors(levs, cols, extend='both')

# draw scatter plot
sc = scax.scatter(zt, bt+ht, c=at, cmap=cmap, norm=norm, alpha=0.75)
scax.set_xlabel('observed trimline elevation (m)')
scax.set_ylabel('compensated LGM surface elevation (m)')


# Histogram axes
# --------------

# diff between compensated surface elevation and trimlines
dt = bt + ht - zt

# add histogram
step = 100.0
bmin = dt.min() - dt.min() % step
bmax = dt.max() - dt.max() % step + step
bins = np.arange(bmin, bmax+step, step)
hsax.hist(dt, bins=bins, color='C1', orientation='horizontal', alpha=0.75)
hsax.set_xlabel('frequency')
hsax.set_ylabel('difference (m)')
hsax.yaxis.set_label_position("right")
hsax.yaxis.tick_right()

# highlight mean difference
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


# Map axes
# --------

# load aggregated data
with ut.io.load_postproc('alpcyc.1km.epic.pp.agg.nc') as ds:
    btp = ds.maxthkbtp
    srf = ds.maxthksrf
    ext = ds.maxthksrf.notnull()

    # plot cold-based areas at max thickness age
    btp.plot.contourf(ax=ax, add_colorbar=False, alpha=0.5, colors=['w']*2,
                      hatches=['////', ''], levels=[-50.0, -1e-3, 0.0])
    btp.plot.contour(ax=ax, colors='0.25', levels=[-1e-3],
                     linestyles='-', linewidths=0.25)
    srf.plot.contour(ax=ax, colors='0.25', levels=ut.pl.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors='0.25', levels=ut.pl.utlevs,
                     linewidths=0.25)
    ext.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors='w',
                      extend='neither', levels=[0.5, 1.5], linewidths=0.25)
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.25)

# remove xarray auto title
ax.set_title('')

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add text labels
kw = dict(ha='center', va='center', transform=ut.pl.ll)
ax.text(6.865, 45.834, 'Mont\nBlanc', **kw)
ax.text(7.659, 45.976, 'Matter-\nhorn', **kw)
ax.text(7.867, 45.937, 'Monte\nRosa', **kw)
ax.text(7.963, 46.537, 'Jungfrau', **kw)
#ax.text(8.126, 46.537, 'Finsternaarhorn', **kw)
ax.text(7.367, 46.233, 'Rhone', rotation=30, **kw)

# draw trimlines
sc = ax.scatter(xt, yt, c=at, cmap=cmap, norm=norm, s=4**2, alpha=0.75)

# add colorbar
cb = ut.pl.add_colorbar(sc, cax)
cb.set_label(r'age (ka)')

# save figure
ut.pl.savefig()
