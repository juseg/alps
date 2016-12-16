#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax = ut.pl.subplots_ts()

# read trimlines data
trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                          dtype=None, delimiter=',', names=True)

xt = trimlines['x']
yt = trimlines['y']
zt = trimlines['z']

# convert to UTM 32
xt, yt, zt = ut.pl.utm.transform_points(ut.pl.swiss, xt, yt, zt).T

# load boot topo
nc = ut.io.load('input/boot/alps-srtm+gou11simi-1km.nc')
b = nc.variables['topg'][:]
nc.close()

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
h = nc.variables['thk'][:].max(axis=0)
#w = nc.variables['tempicethk_basal'][:].max(axis=0)
nc.close()

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
hm = h[i, j]
#wm = w[i, j]

# draw scatter plot
ax.scatter(zt, zt+hm, c=ut.pl.palette['darkblue'], alpha=0.75)
#ax.scatter(zt, zt+wm, c=ut.pl.palette['darkred'], alpha=0.75)
ax.set_xlabel('observed trimline elevation (m)')
ax.set_ylabel('modelled surface elevation (m)', labelpad=2)
ax.set_xlim(1900, 3300)
ax.set_ylim(1750, 4750)

# compute linear fit
c = np.polyfit(zt, zt+hm, 1)
p = np.poly1d(c)
ztfit = np.array([2000, 3200])
zmfit = p(ztfit)
ax.plot(ztfit, ztfit, c='k')
ax.plot(ztfit, zmfit, c=ut.pl.palette['darkblue'], zorder=0)
ax.text(ztfit[-1], ztfit[-1]+50.0, '1:1', ha='right')

# add equation and mean diff
eqn = '$z_m = %.3f \cdot z_t %.3f$' % tuple(c)
diff = hm.mean()
note = '%s\n\nmean difference: %.3f m' % (eqn, diff)
ax.text(0.95, 0.05, note, ha='right', color=ut.pl.palette['darkblue'],
        transform=ax.transAxes)

# save figure
fig.savefig('trimlines')
