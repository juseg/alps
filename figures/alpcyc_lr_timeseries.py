#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize time-series figure
fig, (ax1, ax2) = ut.pl.subplots_ts(2, 1, figw=175.0, figh=85.0, labels=False)
ut.pl.add_subfig_label('(a)', ax=ax1)
ut.pl.add_subfig_label('(b)', ax=ax2, y=0.3)

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    dt = ut.alpcyc_offsets[i]
    c = ut.alpcyc_colours[i]

    # load temperature time series
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    nc = ut.io.load('input/dt/%s.nc' % dtfile)
    age = -nc.variables['time'][:]/1e3
    dt = nc.variables['delta_T'][:]
    nc.close()

    # plot time series
    ax1.plot(age, dt, c=c, alpha=0.75)

    # load output time series
    nc = ut.io.load('output/e9d2d1f/alps-wcnn-2km/%s+%s/'
                    'y???????-ts.nc' % (dtfile, conf))
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # plot time series
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
ut.pl.savefig()
