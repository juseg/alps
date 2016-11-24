#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
records = ['epica', 'epica']
configs = ['', '+esia5']
offsets = [9.2, 9.5]
colors = ['#e31a1c']*2 + ['#1f78b4']*2
styles = [(0, [3, 1]), '-']
dt = 9.5

# initialize time-series figure
fig, ax = ut.pl.subplots_ts()

# for each record
for i, rec in enumerate(records):
    conf = configs[i]
    dt = offsets[i]
    c = colors[i]
    s = styles[i]

    # load output time series
    nc = ut.io.load('output/0.7.3/alps-wcnn-5km/'
                    '%s3222cool%04d+acyc1%s/y0120000-ts.nc'
                    % (rec, round(dt*100), conf))
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # plot time series
    esia = {'': 2, '+esia5': 5}[conf]
    label = rec.upper() + ', $E_{SIA} = %d$, %.1f K' % (esia, dt)
    ax.plot(age, vol, c=c, ls=s, label=label)

# set axes properties and save time series
ax.set_xlim(120, 0)
ax.set_ylim(-0.05, 0.35)
ax.set_ylabel('ice volume (m s.l.e.)')
ax.set_xlabel('model age (ka)')
ax.locator_params(axis='y', nbins=6)
ax.legend(loc='best')
ax.grid(axis='y')
fig.savefig('timeseries')
