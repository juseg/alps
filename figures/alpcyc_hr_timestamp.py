#!/usr/bin/env python
# coding: utf-8

import hyoga.open
import util
import numpy as np
import xarray as xr

# initialize figure
fig, ax = util.fig.subplots_ts()

# plot cumulative time stamp
with pismx.open.dataset('../data/processed/alpcyc.1km.epic.pp.tms.nc') as ds:
    ts = ds.timestamp
    dt = ts.diff('age')
    ts = dt.where(dt > 0.0, ts[1:]).cumsum()/24.0
    ax.plot(ts.age, ts, color='C1')

# set axes properies
ax.invert_xaxis()
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')

# save
util.com.savefig()
