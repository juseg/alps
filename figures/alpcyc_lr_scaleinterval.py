#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
records = ['GRIP', 'EPICA', 'MD01-2444']
offsets = [7.6, 9.5, 8.0]
intends = np.arange(80.0, 0.1, -1.0)
intlens = np.arange(1.0, 40.0, 1.0)

# initialize figure
fig, ax = ut.pl.subplots_ts(1, 1)

# initialize data array
dtavg = np.zeros((3, len(intends), len(intlens)))

# load temperature time series
for i, rec in enumerate(records):
    dt = offsets[i]
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    nc = ut.io.load('input/dt/%s.nc' % dtfile)
    age = -nc.variables['time'][:]/1e3
    dlt = nc.variables['delta_T'][:]
    nc.close()

    # compute average offset on each interval
    dtavg[i] = np.array([[dlt[(a0>age)*(age>a1)].mean() for a0 in intlens+a1]
                                                        for a1 in intends])

# compute average and spread
avgavg = dtavg.mean(axis=0)
#spread = dtavg.max(axis=0)-dtavg.min(axis=0)
spread = dtavg.std(axis=0)  # std instead of max-min
spread /= abs(avgavg)  # relative spread

# plot spread
#ax.contour(intends, intlens, avgavg.T, colors='k')
#ax.contourf(intends, intlens, spread.T, vmin=0.0, vmax=1.0)
ax.pcolormesh(intends, intlens, spread.T, vmin=0.0, vmax=0.25)
ax.set_xlim(intends[-1], intends[0])
ax.set_ylim(intlens[0], intlens[-1])
ax.set_ylabel('interval lenght (ka)')
ax.set_xlabel('interval end (ka)')

# find minimal spread
i, j = np.unravel_index(spread.argmin(), spread.shape)
optend = intends[i]
optlen = intlens[j]
ax.plot(optend, optlen, 'o')

# plot choosen interval
ax.plot(22, 32-22, 'ko')

# save
fig.savefig('alpcyc_lr_scaleinterval')
