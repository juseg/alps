#!/usr/bin/env python
# coding: utf-8

import hyoga.open
import util

# initialize figure
fig, ax = util.fig.subplots_ts()

# for each record
for i, rec in enumerate(util.alpcyc_records):
    label = util.alpcyc_clabels[i]
    conf = util.alpcyc_configs[i]
    pp = 'pp' if 'pp' in conf else 'cp'
    c = util.alpcyc_colours[i]

    # plot cumulative time stamp
    filename = 'alpcyc.2km.{}.{}.tms.nc'.format(rec.lower()[:4], pp)
    with hyoga.open.dataset('../data/processed/'+filename) as ds:
        ts = ds.timestamp
        dt = ts.diff('age')
        ts = dt.where(dt > 0.0, ts[1:]).cumsum()/24.0
        ax.plot(ts.age, ts, color=c, label=label)

# set axes properies
ax.invert_xaxis()
ax.legend(loc='best')
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')

# save
util.com.savefig()
