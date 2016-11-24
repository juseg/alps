#!/usr/bin/env python2
# coding: utf-8

import util as ut
import glob
import numpy as np

# parameters
basedir = '/home/juliens/pism/output/0.7.3/alps-wcnn-1km/scalabilitytest'
preferred = 16

# initialize figure
fig, grid = ut.pl.subplots_ts(3, 1)
ax1, ax2, ax3 = grid

# for each compiler
for comp, c in zip(['gnu', 'intel'], [ut.pl.palette['darkred'], ut.pl.palette['darkblue']]):

    # with and without hyperthreading
    for ntasks, ls in zip([36, 72], ['-', ':']):

        # find all log files
        pattern = '%s/%s-n???-t%2d.err' % (basedir, comp, ntasks)
        filenames = glob.glob(pattern)
        filenames.sort()
        nnodes = []
        wtimes = []

        # if no files, continue
        if len(filenames) == 0:
            continue

        # get simulation time
        for j, filename in enumerate(filenames):

            # read the last two lines
            with open(filename, 'r') as f:
                line = f.readline()

            # retrieve simulation time
            basename = filename.split('/')[-1]
            nnodes.append(int(basename.split('-')[1][1:]))
            wtimes.append(float(line)/3600.0)

        # compute speedup and efficiency
        nnodes = np.asarray(nnodes)  # number of nodes
        wtimes = np.asarray(wtimes)  # wall clock time in hours
        utimes = wtimes*nnodes       # computing time in node-hours
        speedup = wtimes[0]/wtimes   # speed gain sompared to one proc
        efficiency = speedup*nnodes[0]/nnodes

        # plot
        #print 'nodes: %s' % nnodes
        label='%s, %2d tasks per node' % (comp, ntasks)
        ax1.plot(nnodes, wtimes, c=c, ls=ls, marker='|', label=label)
        ax2.plot(nnodes, speedup, c=c, ls=ls, marker='|', label=label)
        ax3.plot(nnodes, efficiency, c=c, ls=ls, marker='|', label=label)

# set common axes properties
for ax in grid:
    ax.set_xscale('log')
    ax.grid()

# scales
ax1.set_yscale('log')
ax2.set_yscale('log')
ax1.set_xlim(1e0, 3e2)

# set axes labels
ax1.set_ylabel('real time (h)')
ax2.set_ylabel('speedup')
ax3.set_ylabel('efficiency')
ax3.set_xlabel('compute nodes (8 cores each)')
ax3.legend(loc='best')

# add ideal speedup curve
ax2.plot([1e0, 1e3], [1e0, 1e3], color='0.5')
angles = np.asarray([45])
points = np.asarray([[2e1, 2e1]])
angles = ax2.transData.transform_angles(angles, points)
ax2.text(points[0,0], points[0,1], 'ideal speedup', color='0.5',
         ha='center', va='bottom', rotation=angles[0])

# add subfigure labels
ax1.text(0.04, 0.92, '(a)', fontweight='bold', transform=ax1.transAxes)
ax2.text(0.04, 0.92, '(b)', fontweight='bold', transform=ax2.transAxes)
ax3.text(0.04, 0.92, '(c)', fontweight='bold', transform=ax3.transAxes)

# save
fig.savefig('scalability')
