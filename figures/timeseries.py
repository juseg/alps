#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

res = '10km'

# initialize time-series figure
figw, figh = 120.0, 80.01
fig, ax = ut.pl.subplots_mm(nrows=1, ncols=1, sharex=True,
                                   figsize=(figw, figh),
                                   left=10.0, right=2.5, bottom=10.0, top=2.5,
                                   wspace=2.5, hspace=2.5)

# loop on offsets
offsets = np.arange(9.0, 10.1, 0.1)
for dt in offsets:

    # load output time series
    filepath = ('output/0.7.3/alps-wcnn-5km/'
                'epica3222cool%04d+acyc1+esia5/y???????-ts.nc' % (round(dt*100)))
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # get maximum
    lgm = age[np.argmax(vol)]

    # plot time series
    ax.plot(age, vol, label='%.01f, %.01f' % (dt, lgm))

# mark true MIS stages
# source: http://www.lorraine-lisiecki.com/LR04_MISboundaries.txt
#ax2.axvspan(71, 57, fc='0.85', lw=0.25)
#ax2.axvspan(29, 14, fc='0.85', lw=0.25)
#ax2.text((120+71)/2, 4.5, 'MIS 5', ha='center')
#ax2.text((71+57)/2, 0.5, 'MIS 4', ha='center')
#ax2.text((57+29)/2, 8.5, 'MIS 3', ha='center')
#ax2.text((29+14)/2, 0.5, 'MIS 2', ha='center')
#ax2.text((14+0)/2, 8.5, 'MIS 1', ha='center')

# set axes properties and save time series
ax.set_xlim(30, 10)
ax.set_ylabel('ice volume (m s.l.e.)')
ax.set_xlabel('model age (ka)')
ax.grid()
ax.legend(loc='best')
fig.savefig('timeseries')
