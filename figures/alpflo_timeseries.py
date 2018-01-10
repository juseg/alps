#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import iceplotlib.plot as iplt

# parameters
c = ut.pl.palette['darkblue']
versions = ['e9d2d1f', '1.0']
resolutions = ['1km', '500m']
linestyles = ['-', '--']

# initialize time-series figure
figw, figh = 85.0, 60.0
fig, grid = iplt.subplots_mm(nrows=2, ncols=1, figsize=(figw, figh),
                             gridspec_kw=dict(left=12.0, right=12.0,
                                              bottom=9.0, top=1.5,
                                              hspace=4.5, wspace=1.5))
ut.pl.add_subfig_label('(a)', ax=grid[0])
ut.pl.add_subfig_label('(b)', ax=grid[1], y=0.6)
twgrid = [ax.twinx() for ax in grid]

# plot temperature time series
dtfile = 'epica3222cool1220'
for ax in grid:
    ut.pl.plot_dt(ax=ax)
    ax.axvspan(25.0, 24.5, fc='0.9', lw=0.25, zorder=0)

# for each resolution
for i, res in enumerate(resolutions):
    ver = versions[i]
    ls = linestyles[i]

    # load output time series
    runname = 'output/%s/alps-wcnn-%s/%s+alpcyc4+pp/' % (ver, res, dtfile)
    filepath = runname + 'y???????-ts.nc'
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]*100.0
    nc.close()

    # print LGM age
    #print age[vol.argmax()]

    # plot time series
    for ax in twgrid:
        ax.plot(age, vol, c=c, ls=ls, label=res)

# set axes properties
grid[0].set_xlim(120.0, 0.0)  # no need
grid[1].set_xlim(25.05, 24.45)
grid[0].set_ylim(-17.5, 2.5)  # no need
grid[1].set_ylim(-14.5, -10.5)
twgrid[0].set_ylim(-5.0, 35.0)
twgrid[1].set_ylim(28.5, 32.5)
twgrid[0].set_ylabel('ice volume (cm s.l.e.)')
twgrid[1].set_ylabel('ice volume (cm s.l.e.)')
ax.legend()

# save
ut.pl.savefig()
