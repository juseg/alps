#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax = ut.pl.subplots_ts()

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    pp = 'pp' if 'pp' in conf else 'cp'
    c = ut.alpcyc_colours[i]

    # plot cumulative time stamp
    filename = 'alpcyc.2km.{}.{}.tms.nc'.format(rec.lower()[:4], pp)
    with ut.io.load_postproc(filename) as ds:
        ts = ds.timestamp
        dt = ts.diff('age')
        ts = dt.where(dt > 0.0, ts[1:]).cumsum()/24.0
        ax.plot(ts.age/1e3, ts, color=c, label=label)

# set axes properies
ax.grid()
ax.invert_xaxis()
ax.legend(loc='best')
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')

# save
ut.pl.savefig()
