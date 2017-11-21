#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax = ut.pl.subplots_ts()

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    dt = ut.alpcyc_offsets[i]
    c = ut.alpcyc_colours[i]

    # load output time series
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    filepath = 'output/e9d2d1f/alps-wcnn-2km/%s+%s/y???????-extra.nc' % (dtfile, conf)
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(365.0*24*60*60*1000)
    stamp = nc.variables['timestamp'][:]
    nc.close()

    # calculate computing speed and node hours
    speed = stamp - np.insert(stamp[:-1], 0, 0.0)
    speed = np.where(speed>0, speed, stamp)
    cumnh = speed.cumsum()/24.0

    # plot
    ax.plot(age, cumnh, color=c, label=label)

# set axes properies
ax.set_xlim(120.0, 0.0)
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')
ax.grid()
ax.legend(loc='best')

# save
ut.pl.savefig()
