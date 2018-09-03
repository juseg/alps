#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize time-series figure
fig, (ax1, ax2) = ut.pl.subplots_ts(2, 1, mode='page', labels=False)
ut.pl.add_subfig_label('(a)', ax=ax1)
ut.pl.add_subfig_label('(b)', ax=ax2, y=0.3)

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    c = ut.alpcyc_colours[i]

    # plot temperature time series
    prefix = 'alpcyc.2km.' + rec.lower()[:4] + ['.cp', '.pp']['pp' in conf]
    with ut.io.load_postproc(prefix + '.dt.nc') as ds:
        ds.delta_T.plot(ax=ax1, c=c, alpha=0.75)

    # plot output time series
    with ut.io.load_postproc(prefix + '.ts.10a.nc') as ds:
        ds.slvol.plot(ax=ax2, c=c, label=label)

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
