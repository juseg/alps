#!/usr/bin/env python
# coding: utf-8

import util
import os
import numpy as np

# initialize figure
fig, grid = util.fig.subplots_ts(3, 1)
ax1, ax2, ax3 = grid

# find all log files
nnodes = []
wtimes = []

# get simulation time
for n in [2, 6, 12, 24, 54, 96, 150]:

    filename = (util.alpflo_bestrun+'sctest%03d' % n)
    filename = os.path.join(os.environ['HOME'], 'pism', filename)
    start = os.stat(filename + '.err').st_mtime
    end = os.stat(filename + '.log').st_mtime
    hours = (end-start) / 3600.0

    # retrieve simulation time
    nnodes.append(n)
    wtimes.append(hours)

# compute speedup and efficiency
nnodes = np.asarray(nnodes)  # number of nodes
wtimes = np.asarray(wtimes)  # wall clock time in hours
utimes = wtimes*nnodes       # computing time in node-hours
speedup = wtimes[0]/wtimes   # speed gain sompared to one proc
efficiency = speedup*nnodes[0]/nnodes

# plot
ax1.plot(nnodes, wtimes, 'C0|-')
ax2.plot(nnodes, speedup, 'C0|-')
ax3.plot(nnodes, efficiency, 'C0|-')

# mark preferred
#c = l.get_color()
i = np.argwhere(nnodes == 24)
label = '%d nodes, %.2f h' % (nnodes[i], wtimes[i])
ax1.plot(nnodes[i], wtimes[i], 'C0o')
ax2.plot(nnodes[i], speedup[i], 'C0o')
ax3.plot(nnodes[i], efficiency[i], 'C0o')
ax1.text(nnodes[i]*1.1, wtimes[i]+0.05, label, color='C0')

# add axes grid
for ax in grid:

# set scales
ax1.set_xscale('log')
ax1.set_yscale('log')
ax2.set_yscale('log')

# set axes labels
ax1.set_ylabel('real time (h)')
ax2.set_ylabel('speedup')
ax3.set_ylabel('efficiency')
ax3.set_xlabel('compute nodes (36 cores each)')

# add ideal speedup curve
sideal = nnodes / float(nnodes[0])
ax2.plot(nnodes, sideal, color='0.5')
angle = ax2.transData.transform_angles(np.array([45.0]),
                                       np.array([[1.0, 1.0]]))[0]
ax2.text(20.0, 30.0, 'ideal speedup', color='0.5', rotation=angle)

# save
util.com.savefig()
