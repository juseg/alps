#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import xarray as xr

# initialize figure
fig, ax = ut.pl.subplots_ts()

# plot cumulative time stamp
with ut.io.load_postproc('alpcyc.1km.epic.pp.tms.nc') as ds:
    ts = ds.timestamp
    dt = ts.diff('age')
    ts = dt.where(dt > 0.0, ts[1:]).cumsum()/24.0
    ts.plot(ax=ax, color='C1')

# set axes properies
ax.grid()
ax.invert_xaxis()
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')

# save
ut.pl.savefig()
