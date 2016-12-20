#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
records = ['GRIP', 'EPICA', 'EPICA', 'MD01-2444']
configs = ['+esia5', '', '+esia5', '+esia5']
colors = ['darkblue', 'lightred', 'darkred', 'darkgreen']
colors = [ut.pl.palette[c] for c in colors]
target = 185.0  # LGM extent 149027.868048 km2, hole-filled 216953.838 km2

# initialize figure
fig, ax = ut.pl.subplots_ts()

# for each record
for i, rec in enumerate(records):
    conf = configs[i]
    c = colors[i]
    offsets = []
    fpareas = []

    # loop on offsets
    for dt in np.arange(6.0, 10.1, 0.1):

        # try to find max area
        try:

            # load extra file
            dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
            nc = ut.io.load('output/0.7.3/alps-wcnn-5km/%s+acyc1%s/'
                            'y0120000-extra.nc' % (dtfile, conf))
            x = nc.variables['x'][:]
            y = nc.variables['y'][:]
            thk = nc.variables['thk'][909:1059]  # 29 to 14 ka
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
        except (RuntimeError, IndexError):
            pass

    # plot
    esia = {'': 2, '+esia5': 5}[conf]
    label = rec + ', $E_{SIA} = %d$' % esia
    argmin = np.argmin(np.abs(np.array(fpareas)-target))
    ax.plot(offsets, fpareas, c=c, marker='o', label=label)
    ax.plot(offsets[argmin], fpareas[argmin], c=c, marker='D')
    ax.axvline(offsets[argmin], lw=0.1, c=c)
    for dt, a in zip(offsets, fpareas):
        if a:
            ax.text(dt, a+5, '%.0f' % a, color=c, fontsize=4, ha='center',
                    clip_on=True)

# set axes properties
# FIXME: refine limits as new runs become available
ax.axhspan(240.0, 500.0, fc='0.9', lw=0.0, zorder=0)
ax.axhline(target, lw=0.1, c='0.5')
ax.legend(loc='best')
ax.set_xlim(6.9, 10.1)
ax.set_ylim(150.0, 300.0)
ax.set_xlabel('temperature offset (K)')
ax.set_ylabel(r'glaciated area ($10^3\,km^2$)')

# save
fig.savefig('glacareas')
