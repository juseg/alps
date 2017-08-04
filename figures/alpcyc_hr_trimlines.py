#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
figw, figh = 85.0, 60.0
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
ax = fig.add_axes([10.0/figw, 7.5/figh, 50.0/figw, 50.0/figh])
cax = fig.add_axes([12.5/figw, 35.0/figh, 5.0/figw, 20.0/figh])
hsax = fig.add_axes([62.5/figw, 7.5/figh, 20.0/figw, 50.0/figh], sharey=ax)


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
nc.close()

# compute max thickness and its age
lgmage = age[thk.argmax(axis=0)]
maxthk = thk.max(axis=0)

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
ht = maxthk[j, i]
at = lgmage[j, i]


# Scatter axes
# ------------

# set contour levels and colors
mpl = ut.pl.iplt.matplotlib
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]
cmap, norm = mpl.colors.from_levels_and_colors(levs, cols, extend='both')

# draw scatter plot
sc = ax.scatter(zt, ht, c=at, cmap=cmap, norm=norm, alpha=0.75)
ax.set_xlabel('observed trimline elevation $z_t$ (m)')
ax.set_ylabel('modelled max ice thickness $h_t$ (m)', labelpad=2)

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
hsax.set_xlabel('freq.')
[l.set_visible(False) for l in hsax.get_yticklabels()]

# highlight mean thickness
havg = ht.mean()
ax.axhline(havg, c=ut.pl.palette['darkblue'])
hsax.axhline(havg, c=ut.pl.palette['darkblue'])
hsax.text(2.0, havg+25.0, '%.0f m' % havg, color=ut.pl.palette['darkblue'])

# save figure
fig.savefig('alpcyc_hr_trimlines')
