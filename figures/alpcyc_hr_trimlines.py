#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure (one column)
figw, figh = 85.0, 115.0
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
ax = fig.add_axes([2.5/figw, 2.5/figh, 80.0/figw, 80.0*2/3/figh], projection=ut.pl.utm)
cax = fig.add_axes([12.5/figw, (80.0*2/3-2.5)/figh, 30.0/figw, 2.5/figh])
scax = fig.add_axes([10.0/figw, 65.0/figh, 45.0/figw, 47.5/figh])
hsax = fig.add_axes([57.5/figw, 65.0/figh, 25.0/figw, 47.5/figh], sharey=scax)

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

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
mis = (age < 29.0) * (age >= 14.0)
age = age[mis]
thk = nc.variables['thk'][mis]
srf = nc.variables['usurf'][mis]
tpa = nc.variables['temppabase'][mis]
nc.close()

# compute max thickness and its age
lgmage = age[thk.argmax(axis=0)]
maxthk = thk.max(axis=0)
maxsrf = srf.max(axis=0)
mask = (thk < 1.0).prod(axis=0)
maxsrf = np.ma.masked_where(mask, maxsrf)

# compute duration of warm-based coved
dt = age[0] - age[1]
warm = ((thk >= 1.0)*(tpa >= -1e-3)).sum(axis=0)*dt
warm = np.ma.masked_where(mask, warm)

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
sc = scax.scatter(zt, ht, c=at, cmap=cmap, norm=norm, alpha=0.75)
scax.set_xlabel('observed trimline elevation (m)')
scax.set_ylabel('modelled maximum ice thickness (m)', labelpad=2)


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

# Map axes
# --------

# plot boot topo
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
im = nc.imshow('topg', ax, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
boot = nc.variables['topg'][:]
nc.close()

# plot areas with less than 1 ka warm ice cover
im = ax.contourf(x, y, warm, levels=[0.0, 1.0, 120.0], colors=['w', 'w'],
                 hatches=['////', ''], alpha=0.5)
cs = ax.contour(x, y, warm, [1.0], colors='0.25', linewidths=0.25)
cs = ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.25)

# add ice mask and contour levels
ax.contourf(x, y, mask, levels=[-0.5, 0.5], colors='w', alpha=0.75)
ax.contour(x, y, maxsrf, ut.pl.inlevs, colors='0.25', linewidths=0.1)
ax.contour(x, y, maxsrf, ut.pl.utlevs, colors='0.25', linewidths=0.25)

# draw trimlines
sc = ax.scatter(xt, yt, c=at, cmap=cmap, norm=norm, s=4**2, alpha=0.75)

# add colorbar
cb = fig.colorbar(sc, cax, orientation='horizontal')
cb.set_label(r'age (ka)')

# save figure
fig.savefig('alpcyc_hr_trimlines')
