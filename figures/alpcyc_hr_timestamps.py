#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax = ut.pl.subplots_ts()

# open extra file
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(365.0*24*60*60*1000)
stamp = nc.variables['timestamp'][:]
nc.close()

# calculate computing speed and node hours
speed = stamp - np.insert(stamp[:-1], 0, 0.0)
speed = np.where(speed>0, speed, stamp)
cumnh = speed.cumsum()/24.0

# plot
c = ut.pl.palette['darkblue']
ax.plot(age, cumnh, color=c)

# mark scalability test
#testage = 120.0 - 57.5
#ax.plot(testage, cumnh[age == testage], color=c, marker='o')
#ax.text(testage, cumnh[age == testage]+0.5, 'scalability test  ', color=c, ha='right')

# set axes properies
ax.set_xlim(120.0, 0.0)
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')
ax.grid()

# save
fig.savefig('alpcyc_hr_timestamps')
