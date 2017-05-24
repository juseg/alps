#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# LGM extent UTM 32
# original?  9304663497.36 m2
# holefilled 9698970454.26 m2
# fullfilled 9920070286.36 m2
target = 9.92007028636

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
            dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
            nc = ut.io.load('output/e9d2d1f/alps-wcnn-5km/%s+%s/'
                            'y0120000-extra.nc' % (dtfile, conf))
            x = nc.variables['x'][61:90]
            y = nc.variables['y'][82:101]
            thk = nc.variables['thk'][909:1059, 82:101, 61:90]  # 29 to 14 ka
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

    # continue if no files found
    if fpareas == []:
        continue

    # plot
    argmin = np.argmin(np.abs(np.array(fpareas)-target))
    #print label, offsets[argmin]
    ax.plot(offsets, fpareas, c=c, marker='o', label=label)
    ax.plot(offsets[argmin], fpareas[argmin], c=c, marker='D')
    ax.axvline(offsets[argmin], lw=0.1, c=c)
    for dt, a in zip(offsets, fpareas):
        if a:
            ax.text(dt, a+0.25, '%.1f' % a, color=c, fontsize=4, ha='right',
                    clip_on=True)

# set axes properties
ax.axhline(target, lw=0.1, c='0.5')
ax.legend(loc='upper left', ncol=3)
ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1]+0.25)
ax.set_xlabel('temperature offset (K)')
ax.set_ylabel(r'glaciated area ($10^3\,km^2$)')

# save
fig.savefig('alpcyc_lr_rhineareas')
