#!/usr/bin/env python
# coding: utf-8

import util
import numpy as np
import xarray as xr

# initialize figure
fig, ax = util.fig.subplots_ts()

# plot cumulative time stamp
with util.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.tms.nc') as ds:
    ts = ds.timestamp
    dt = ts.diff('time')
    ts = dt.where(dt > 0.0, ts[1:]).cumsum()/24.0
    ax.plot(ts.age/1e3, ts, color='C1')

# set axes properies
ax.grid()
ax.invert_xaxis()
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')

# save
util.pl.savefig()
