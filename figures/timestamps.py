#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax = ut.pl.subplots_ts()

# open extra file
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(365.0*24*60*60*1000)
stamp = nc.variables['timestamp'][:]
nc.close()

# calculate computing speed and node hours
speed = stamp - np.insert(stamp[:-1], 0, 0.0)
speed = np.where(speed>0, speed, stamp)
cumnh = speed.cumsum()*16e-3

# plot
ax.plot(age, cumnh)
ax.set_xlim(120.0, 0.0)

# add labels
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (node-hours*1000)')
ax.grid()

# add legend and save
fig.savefig('timestamps')
