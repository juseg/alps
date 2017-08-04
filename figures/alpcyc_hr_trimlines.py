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
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
b = nc.variables['topg'][:]
nc.close()

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
h = nc.variables['thk'][:].max(axis=0)
nc.close()

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
ht = h[j, i]

# draw scatter plot
ax.scatter(zt, ht, c=ut.pl.palette['darkblue'], alpha=0.75)
ax.set_xlabel('observed trimline elevation $z_t$ (m)')
ax.set_ylabel('modelled max ice thickness $h_t$ (m)', labelpad=2)

# compute linear fit
c = np.polyfit(zt, ht, 1)
p = np.poly1d(c)
ztfit = np.array([2000, 3200])
htfit = p(ztfit)
ax.plot(ztfit, htfit, c=ut.pl.palette['darkblue'], zorder=0)

# add equation and mean diff
eqn = '$h_t = %.3f \cdot z_t + %.3f$' % tuple(c)
diff = ht.mean()
note = '%s\n\nmean difference: %.3f m' % (eqn, diff)
ax.text(0.95, 0.05, note, ha='right', color=ut.pl.palette['darkblue'],
        transform=ax.transAxes)

# save figure
fig.savefig('alpcyc_hr_trimlines')
