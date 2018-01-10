#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
versions = ['e9d2d1f', '1.0']
resolutions = ['1km', '500m']
linestyles = ['-', '--']

# initialize time-series figure
fig, grid = ut.pl.subplots_ts(2, 1)

# load temperature time series
dtfile = 'epica3222cool1220'
nc = ut.io.load('input/dt/%s.nc' % dtfile)
age = -nc.variables['time'][:]/1e3
dt = nc.variables['delta_T'][:]
nc.close()

# plot time series
ax = grid[0]
ax.plot(age, dt)

# set axes properties
ax.set_ylabel('temperature offset (K)')
ax.set_ylim(-14.5, -10.5)
ax.grid(axis='y')
ax.locator_params(axis='y', nbins=6)

# for each resolution
for i, res in enumerate(resolutions):
    ver = versions[i]

    # load output time series
    runname = 'output/%s/alps-wcnn-%s/%s+alpcyc4+pp/' % (ver, res, dtfile)
    filepath = runname + 'y???????-ts.nc'
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]*100.0
    nc.close()

    # plot time series
    ax = grid[1]
    ax.plot(age, vol, label=res)

# set axes properties
ax.set_xlim(25.05, 24.45)
ax.set_ylim(28.5, 31.5)
ax.set_ylabel('ice volume (cm s.l.e.)')
ax.set_xlabel('model age (ka)')
ax.legend()
ax.grid(axis='y')
ax.locator_params(axis='y', nbins=6)

# save
ut.pl.savefig()
