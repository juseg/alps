#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
# FIXME: refine offsets
records = ['GRIP', 'EPICA', 'EPICA', 'MD01-2444']
configs = ['+esia5', '', '+esia5', '+esia5']
offsets = [7.5, 9.2, 9.5, 8.0]
colors = ['darkblue', 'lightred', 'darkred', 'darkgreen']
colors = [ut.pl.palette[c] for c in colors]

# initialize time-series figure
fig, (ax1, ax2) = ut.pl.subplots_ts(2, 1, figw=170.0)

# for each record
for i, rec in enumerate(records):
    conf = configs[i]
    dt = offsets[i]
    c = colors[i]

    # load temperature time series
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    nc = ut.io.load('input/dt/%s.nc' % dtfile)
    age = -nc.variables['time'][:]/1e3
    dt = nc.variables['delta_T'][:]
    nc.close()

    # plot time series
    ax1.plot(age, dt, c=c, alpha=0.75)

    # load output time series
    nc = ut.io.load('output/0.7.3/alps-wcnn-5km/%s+acyc1%s/y0120000-ts.nc'
                    % (dtfile, conf))
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # plot time series
    esia = {'': 2, '+esia5': 5}[conf]
    label = rec.upper() + ', $E_{SIA} = %d$' % esia
    ax2.plot(age, vol, c=c, label=label)

# add marine isotope stages
ut.pl.plot_mis(ax=ax2, y=0.925)

# set axes properties and save time series
ax1.set_xlim(120, 0)
ax1.set_ylim(-12.5, 7.5)
ax2.set_ylim(-0.05, 0.35)
ax1.set_ylabel('temperature offset (K)')
ax2.set_ylabel('ice volume (m s.l.e.)')
ax2.set_xlabel('model age (ka)')
ax1.grid(axis='y')
ax2.grid(axis='y')
ax2.legend(loc='best')
ax1.locator_params(axis='y', nbins=6)
ax2.locator_params(axis='y', nbins=6)

# save
fig.savefig('timeseries')
