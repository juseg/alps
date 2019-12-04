#!/usr/bin/env python
# coding: utf-8

import util

# initialize time-series figure
fig, (ax1, ax2) = util.fig.subplots_ts(2, 1, mode='page', labels=False)
util.fig.add_subfig_label('(a)', ax=ax1)
util.fig.add_subfig_label('(b)', ax=ax2, y=0.3)

# for each record
for i, rec in enumerate(util.alpcyc_records):
    label = util.alpcyc_clabels[i]
    conf = util.alpcyc_configs[i]
    c = util.alpcyc_colours[i]

    # plot temperature time series
    prefix = 'alpcyc.2km.' + rec.lower()[:4] + ['.cp', '.pp']['pp' in conf]
    with util.io.open_dataset('../data/processed/'+prefix + '.dt.nc') as ds:
        ax1.plot(ds.age/1e3, ds.delta_T, c=c, alpha=0.75)

    # plot output time series
    with util.io.open_dataset('../data/processed/'+prefix + '.ts.10a.nc') as ds:
        ax2.plot(ds.age/1e3, ds.slvol, c=c, label=label)

# add marine isotope stages
# FIXME move this to figure creation
util.fig.plot_mis(ax=ax2, y=0.925)

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
util.pl.savefig()
