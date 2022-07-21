#!/usr/bin/env python
# Copyright (c) 2016-2022, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import hyoga.open
import util
import numpy as np

# LGM ice extent in UTM 32
# * Entire Alps
#  - E&G original data:     131.679803 10^3km2
#  - selected holes filled: 149.027868
#  - all the holes filled:  150.102315
# * Rhine lobe 5 km
#  - E&G original data:      9.30466349736 10^3 km2
#  - selected holes filled:  9.69897045426
#  - all the holes filled:   9.92007028636
# * Rhine lobe 2 km
#  - E&G original data:      9.66219615876
#  - selected holes filled: 10.06855769962
#  - all the holes filled:  10.29263599490
target = 10.29263599490

# initialize figure
fig, ax = util.fig.subplots_ts()

# resolutions and styles
resolutions = ['5km', '2km']
linestyles = [':', '-']
linewidths = [0.5, 1.0]
markers = ['+', '*']

# domain for masking
w, e, s, n = util.fig.regions['rhlobe']

# for each record
for i, rec in enumerate(util.alpcyc_records):
    label = util.alpcyc_clabels[i]
    conf = util.alpcyc_configs[i]
    c = util.alpcyc_colours[i]
    offsets = []
    fpareas = []

    # loop on offsets
    for dt in np.arange(6.0, 14.1, 0.1):

        # try to find max area
        try:

            # load extra file
            with hyoga.open.mfdataset(
                '~/pism/output/e9d2d1f/alpcyc4.2km.{}.{:04.0f}/ex.???????.nc'.format(
                    rec.replace('-', '').lower(), 100*dt, conf)) as ds:

                # select space-time of interest
                thk = ds.thk.loc[29e3:14e3, s:n, w:e]

                # compute glaciated area in 1e3 km2
                dx = ds.x[1] - ds.x[0]
                dy = ds.y[1] - ds.y[0]
                footprint = 1 - (thk < 1.0).prod(axis=0)
                area = footprint.sum()*dx*dy*1e-9

            # append to lists
            offsets.append(dt)
            fpareas.append(area)

        # else do nothing
        except (IOError):
            pass

    # continue if no files found
    if fpareas == []:
        continue

    # plot
    argmin = np.argmin(np.abs(np.array(fpareas)-target))
    ax.plot(offsets, fpareas, c=c, marker='+', label=label)
    ax.axhline(target, lw=0.1, c='0.5')
    ax.plot(offsets[argmin], fpareas[argmin], c=c, marker='D')
    ax.axvline(offsets[argmin], lw=0.1, c=c)
    for dt, a in zip(offsets, fpareas):
        if a:
            ax.text(dt+0.1, a, '%.1f' % a, color=c, fontsize=4,
                    ha='left', va='center', clip_on=True)

# set axes properties
ax.legend(loc='lower left', ncol=3)
ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[1]+0.1)
ax.set_xlabel('temperature offset (K)')
ax.set_ylabel(r'glaciated area ($10^3\,km^2$)')

# save
util.com.savefig()
