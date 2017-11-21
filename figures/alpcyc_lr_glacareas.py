#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# LGM extent UTM 32
# original   131,679.803 km2
# holefilled 149,027.868 km2
# fullfilled 150,102.315 km²
target = 150.102315

# initialize figure
fig, ax = ut.pl.subplots_ts()

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    c = ut.alpcyc_colours[i]
    offsets = []
    fpareas = []

    # loop on offsets
    for dt in np.arange(6.0, 14.1, 0.1):

        # try to find max area
        try:

            # load extra file
            dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(),
                                         round(dt*100))
            nc = ut.io.load('output/e9d2d1f/alps-wcnn-2km/%s+%s/'
                            'y???????-extra.nc' % (dtfile, conf))
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
        except (RuntimeError, IndexError, ValueError):
            pass

    # continue if no files found
    if fpareas == []:
        continue

    # plot
    argmin = np.argmin(np.abs(np.array(fpareas)-target))
    ax.plot(offsets, fpareas, c=c, marker='+', label=label)
    ax.plot(offsets[argmin], fpareas[argmin], c=c, marker='D')
    ax.axvline(offsets[argmin], lw=0.1, c=c)
    for dt, a in zip(offsets, fpareas):
        if a:
            ax.text(dt+0.1, a, '%.0f' % a, color=c, fontsize=4,
                    ha='left', va='center', clip_on=True)

# set axes properties
ax.axhline(target, lw=0.1, c='0.5')
ax.legend(loc='lower left', ncol=3)
ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[1]+0.1)
ax.set_xlabel('temperature offset (K)')
ax.set_ylabel(r'glaciated area ($10^3\,km^2$)')

# save
ut.pl.savefig()
