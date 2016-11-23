#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
t = -1
# initialize figure
figw, figh = 120.01, 80.01
fig, ax = ut.pl.subplots_mm(nrows=1, ncols=1, figsize=(figw, figh),
                            left=10.0, right=2.5, bottom=10.0, top=2.5)

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
ax.plot(age, cumnh, 'b-')
ax.plot(age[-1], cumnh[-1], 'bo')
ax.set_xlim(120.0, 0.0)

# add estimate
ax.plot([20, 10, 0], [20, 24, 25], 'k--')

# add labels
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (node-hours*1000)')
ax.grid()

# add legend and save
fig.savefig('timestamps')
