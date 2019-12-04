#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax = util.fi.subplots_ts()

# for each record
for i, rec in enumerate(util.alpcyc_records):
    label = util.alpcyc_clabels[i]
    conf = util.alpcyc_configs[i]
    pp = 'pp' if 'pp' in conf else 'cp'
    c = util.alpcyc_colours[i]

    # plot cumulative time stamp
    filename = 'alpcyc.2km.{}.{}.tms.nc'.format(rec.lower()[:4], pp)
    with util.io.open_dataset('../data/processed/'+filename) as ds:
        ts = ds.timestamp
        dt = ts.diff('time')
        ts = dt.where(dt > 0.0, ts[1:]).cumsum()/24.0
        ax.plot(ts.age/1e3, ts, color=c, label=label)

# set axes properies
ax.grid()
ax.invert_xaxis()
ax.legend(loc='best')
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')

# save
util.pl.savefig()
