#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
records = ['epica']
configs = ['', '+esia5']
colors = [ut.pl.palette['darkred'], ut.pl.palette['darkblue']]
styles = [(0, [3, 1]), '-']
target = 185.0  # Ehlers and Gibbard is only 149027.868048 km2

# initialize figure
fig, ax = ut.pl.subplots_ts()

# for each record
for rec, c in zip(records, colors):

    # for each config
    for conf, s in zip(configs, styles):
        offsets = []
        fpareas = []

        # loop on offsets
        for dt in np.arange(9.0, 10.1, 0.1):

            # try to find max area
            try:

                # load extra file
                nc = ut.io.load('output/0.7.3/alps-wcnn-5km/'
                                '%s3222cool%04d+acyc1%s/y0120000-extra.nc'
                                % (rec, round(dt*100), conf))
                x = nc.variables['x'][:]
                y = nc.variables['y'][:]
                thk = nc.variables['thk'][:]
                nc.close()

                # compute footprint area in 1e3 km2
                dx = x[1] - x[0]
                dy = y[1] - y[0]
                footprint = 1 - (thk < 1.0).prod(axis=0)
                a = footprint.sum()*dx*dy*1e-9
    
                # append to lists
                offsets.append(dt)
                fpareas.append(a)

            # else do nothing
            except RuntimeError:
                pass

        # plot
        esia = {'': 2, '+esia5': 5}[conf]
        label = rec.upper() + ', $E_{SIA} = %d$' % esia
        argmin = np.argmin(np.abs(np.array(fpareas)-target))
        ax.plot(offsets, fpareas, c=c, ls=s, marker='o', label=label)
        ax.plot(offsets[argmin], fpareas[argmin], c=c, marker='D')
        ax.axvline(offsets[argmin], lw=0.1, c=c, ls=s)
        for dt, a in zip(offsets, fpareas):
            if a:
                ax.text(dt, a+2, '%.2f' % a, color=c, ha='center')

# set axes properties
ax.axhline(target, lw=0.1, c='0.5')
ax.axhspan(240.0, 300.0, fc='0.9', lw=0.25, zorder=0)
ax.legend(loc='best')
ax.set_xlim(8.9, 10.1)
ax.set_ylim(150.0, 290.0)
ax.set_xlabel('temperature offset (K)')
ax.set_ylabel(r'glaciated area ($10^3\,km^2$)')

# save
fig.savefig('glacareas')
