#!/usr/bin/env python
# coding: utf-8

import util
import glob
import os.path
import numpy as np

# initialize figure
fig, ax = util.fi.subplots_ts()

# open extra files
globpath = os.path.join(os.environ['HOME'], 'pism', util.alpflo_bestrun,
                        'y???????-extra.nc')
filelist = glob.glob(globpath)
filelist.sort()

# concatenate timestamps
age = np.array([])
stamp = np.array([])
for filepath in filelist:
    nc = util.io.load(filepath)
    age = np.append(age, -nc.variables['time'][:]/(365.0*24*60*60*1000))
    stamp = np.append(stamp, nc.variables['timestamp'][:])
    nc.close()

# calculate computing speed and node hours
speed = stamp - np.insert(stamp[:-1], 0, 0.0)
speed = np.where(speed>0, speed, stamp)
cumnh = speed.cumsum()/24.0

# plot
c = 'C1'
ax.plot(age, cumnh, color=c)

# mark scalability test
#testage = 120.0 - 57.5
#ax.plot(testage, cumnh[age == testage], color=c, marker='o')
#ax.text(testage, cumnh[age == testage]+0.5, 'scalability test  ', color=c, ha='right')

# set axes properies
#ax.set_xlim(120.0, 0.0)
ax.invert_xaxis()
ax.set_xlabel('model time (ka)')
ax.set_ylabel('computing time (days)')
ax.grid()

# save
util.pl.savefig()
