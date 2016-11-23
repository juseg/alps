#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import numpy as np
import iceplotlib.plot as iplt
import cartopy.crs as ccrs

# geographic projections
ll = ccrs.PlateCarree()
utm = ccrs.UTM(32)
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)

# initialize figure
fig, ax = iplt.subplots_mm(figsize=(85.0, 60.0),
                           left=12.5, right=2.5, bottom=7.5, top=2.5)

# read trimlines data
trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                          dtype=None, delimiter=',', names=True)

xt = trimlines['x']
yt = trimlines['y']
zt = trimlines['z']

# convert to UTM 32
xt, yt, zt = utm.transform_points(swiss, xt, yt, zt).T

# load extra data
filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-1km/'
            'epica3222cool0950+acyc1+esia5/y???????-extra.nc')
nc = iplt.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
z = nc.variables['usurf'][:].max(axis=0)
nc.close()

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
zm = z[i, j]

# draw scatter plot
ax.scatter(zt, zm, c='#1f78b4', alpha=0.75)
ax.set_xlabel('observed trimline elevation (m)')
ax.set_ylabel('maximum ice surface  elevation (m)')
ax.set_xlim(1900, 3300)
ax.set_ylim(1750, 4250)

# compute linear fit
c = np.polyfit(zt, zm, 1)
p = np.poly1d(c)
ztfit = np.array([2000, 3200])
zmfit = p(ztfit)
ax.plot(ztfit, ztfit, c='k')
ax.plot(ztfit, zmfit, c='#1f78b4', zorder=0)
ax.text(ztfit[-1], ztfit[-1]+50.0, '1:1', ha='right')

# add equation and mean diff
eqn = '$z_m = %.3f \cdot z_t %.3f$' % tuple(c)
diff = (zm-zt).mean()
note = '%s\n\nmean difference: %.3f m' % (eqn, diff)
ax.text(0.95, 0.05, note, ha='right', color='#1f78b4', transform=ax.transAxes)

# save figure
fig.savefig('trimlines')
