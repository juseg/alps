#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure (one column)
figw, figh = 85.0, 90.0
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
ax = fig.add_axes([10.0/figw, 57.5/figh, 45.0/figw, 30.0/figh], projection=ut.pl.utm)
cax = fig.add_axes([57.5/figw, 57.5/figh, 5.0/figw, 30.0/figh])
scax = fig.add_axes([10.0/figw, 7.5/figh, 45.0/figw, 47.5/figh])
hsax = fig.add_axes([57.5/figw, 7.5/figh, 25.0/figw, 47.5/figh], sharey=scax)

## initialize figure (full width)
#figw, figh = 170.0, 60.0
#fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
#ax = fig.add_axes([2.5/figw, 2.5/figh, 82.5/figw, 55.0/figh], projection=ut.pl.utm)
#cax = fig.add_axes([5.0/figw, 20.0/figh, 5.0/figw, 30.0/figh])
#scax = fig.add_axes([97.5/figw, 7.5/figh, 50.0/figw, 50.0/figh])
#hsax = fig.add_axes([150.0/figw, 7.5/figh, 17.5/figw, 50.0/figh], sharey=scax)

# prepare map axes
ax.set_rasterization_zorder(2.5)
ax.set_extent(ut.pl.regions['valais'], crs=ax.projection)

# add subfigure labels
ut.pl.add_subfig_label('(a)', ax=ax)
ut.pl.add_subfig_label('(b)', ax=scax)
ut.pl.add_subfig_label('(c)', ax=hsax)


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

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
thk = nc.variables['thk'][:]
srf = nc.variables['usurf'][:]
nc.close()

# compute max thickness and its age
lgmage = age[thk.argmax(axis=0)]
maxthk = thk.max(axis=0)
maxsrf = srf.max(axis=0)
mask = (thk < 1.0).prod(axis=0)

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
ht = maxthk[j, i]
at = lgmage[j, i]


# Map axes
# --------

# set contour levels and colors
mpl = ut.pl.iplt.matplotlib
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]
cmap, norm = mpl.colors.from_levels_and_colors(levs, cols, extend='both')

# plot boot topo
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
im = nc.imshow('topg', ax, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
boot = nc.variables['topg'][:]
nc.close()

# add ice mask and contour levels
ax.contourf(x, y, mask, levels=[-0.5, 0.5], colors='w', alpha=0.75)
ax.contour(x, y, maxsrf, ut.pl.inlevs, colors='0.25', linewidths=0.1)
ax.contour(x, y, maxsrf, ut.pl.utlevs, colors='0.25', linewidths=0.25)

# draw trimlines
ax.scatter(xt, yt, c=at, cmap=cmap, norm=norm, s=4**2, alpha=0.75)


# Scatter axes
# ------------

# draw scatter plot
sc = scax.scatter(zt, ht, c=at, cmap=cmap, norm=norm, alpha=0.75)
scax.set_xlabel('observed trimline elevation $z_t$ (m)')
scax.set_ylabel('modelled max ice thickness $h_t$ (m)', labelpad=2)

# add colorbar
cb = fig.colorbar(sc, cax)
cb.set_label(r'age (ka)')


# Histogram axes
# --------------

# add histogram
step = 100.0
bmin = ht.min() - ht.min() % step
bmax = ht.max() - ht.max() % step + step
bins = np.arange(bmin, bmax+step, step)
hsax.hist(ht, bins=bins, orientation='horizontal', alpha=0.75)
hsax.set_xlabel('frequency')
[l.set_visible(False) for l in hsax.get_yticklabels()]

# highlight mean thickness
havg = ht.mean()
scax.axhline(havg, c='0.25')
hsax.axhline(havg, c='0.25')
hsax.text(2.0, havg+25.0, '%.0f m' % havg, color='0.25')

# save figure
fig.savefig('alpcyc_hr_trimlines')
