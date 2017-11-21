#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp
import matplotlib.colors as mcolors

# initialize figure (one column)
figw, figh = 85.0, 115.0
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
ax = fig.add_axes([2.5/figw, 2.5/figh, 80.0/figw, 80.0*2/3/figh], projection=ut.pl.utm)
cax = fig.add_axes([12.5/figw, (80.0*2/3-2.5)/figh, 30.0/figw, 2.5/figh])
scax = fig.add_axes([12.5/figw, 65.0/figh, 47.5/figw, 47.5/figh])
hsax = fig.add_axes([62.5/figw, 65.0/figh, 10.0/figw, 47.5/figh])

## initialize figure (full width)
#figw, figh = 170.0, 60.0
#fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
#ax = fig.add_axes([2.5/figw, 2.5/figh, 82.5/figw, 55.0/figh], projection=ut.pl.utm)
#cax = fig.add_axes([5.0/figw, 20.0/figh, 5.0/figw, 30.0/figh])
#scax = fig.add_axes([97.5/figw, 7.5/figh, 50.0/figw, 50.0/figh])
#hsax = fig.add_axes([150.0/figw, 7.5/figh, 10.0/figw, 50.0/figh])

# prepare map axes
ax.set_rasterization_zorder(2.5)
ax.set_extent(ut.pl.regions['valais'], crs=ax.projection)

# add subfigure labels
ut.pl.add_subfig_label('(a)', ax=scax)
ut.pl.add_subfig_label('(b)', ax=hsax)
ut.pl.add_subfig_label('(c)', ax=ax)


# Input data
# ----------

# read trimlines data
trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                          dtype=None, delimiter=',', names=True)
xt = trimlines['x']
yt = trimlines['y']
zt = trimlines['z']

# convert to UTM 32
xt, yt, zt = ut.pl.utm.transform_points(ut.pl.swiss, xt, yt, zt).T

# read postprocessed data
maxthksrf, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthksrf')
maxthkage, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthkage')
maxicethk, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxicethk')
warmbased, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'warmbased')

# get coordinates  # FIXME not efficient
filepath = ut.alpcyc_bestrun + 'y0120000-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
nc.close()

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


# Scatter axes
# ------------

# set contour levels and colors
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
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
hsax.hist(ht, bins=bins, orientation='horizontal', alpha=0.75)
hsax.set_xlabel('frequency')
hsax.set_ylabel('difference (m)')
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


# Map axes
# --------

# plot areas with less than 1 ka warm ice cover
im = ax.contourf(warmbased, levels=[0e3, 1e3, 120e3], extent=extent,
                 colors=['w', 'w'], hatches=['////', ''], alpha=0.5)
cs = ax.contour(warmbased, [1e3], extent=extent, colors='0.25', linewidths=0.25)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_envelope(ax, levels=[0e3, 3e3], colors='w')
ut.pl.draw_natural_earth(ax)

# draw trimlines
sc = ax.scatter(xt, yt, c=at, cmap=cmap, norm=norm, s=4**2, alpha=0.75)

# add colorbar
cb = fig.colorbar(sc, cax, orientation='horizontal')
cb.set_label(r'age (ka)')

# save figure
ut.pl.savefig()
