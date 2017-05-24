#!/usr/bin/env python2
# coding: utf-8

import util as ut
import glob
import numpy as np

# parameters
basedir = '/home/juliens/pism/output/0.7.3-craypetsc/alps-wcnn-1km/scalabilitytest'
arches = ['dora-gnu', 'daint-gnu']
colors = [ut.pl.palette[c] for c in ['darkblue', 'darkred']]
preferred = 16

# initialize figure
fig, grid = ut.pl.subplots_ts(3, 1)
ax1, ax2, ax3 = grid

# for each compiler
for arch, c in zip(arches, colors):

    # with and without hyperthreading
    for ntasks, ls in zip([36, 72], ['-', ':']):

        # find all log files
        pattern = '%s/%s-n???-t%2d.err' % (basedir, arch, ntasks)
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
            nnodes.append(int(basename.split('-')[2][1:]))
            wtimes.append(float(line)/3600.0)

        # compute speedup and efficiency
        nnodes = np.asarray(nnodes)  # number of nodes
        wtimes = np.asarray(wtimes)  # wall clock time in hours
        utimes = wtimes*nnodes       # computing time in node-hours
        speedup = wtimes[0]/wtimes   # speed gain sompared to one proc
        efficiency = speedup*nnodes[0]/nnodes

        # plot
        #print 'nodes: %s' % nnodes
        label = '%s, %2d tasks per node' % (arch, ntasks)
        ax1.plot(nnodes, wtimes, c=c, ls=ls, marker='|', label=label)
        ax2.plot(nnodes, speedup, c=c, ls=ls, marker='|', label=label)
        ax3.plot(nnodes, efficiency, c=c, ls=ls, marker='|', label=label)

        # preferred
        if arch == 'daint-gnu' and ntasks == 36:
            idx = np.argwhere(nnodes == preferred)
            label = '%d nodes, %.2f h' % (nnodes[idx], efficiency[idx])
            ax1.plot(nnodes[idx], wtimes[idx], c=c, marker='o')
            ax2.plot(nnodes[idx], speedup[idx], c=c, marker='o')
            ax3.plot(nnodes[idx], efficiency[idx], c=c, marker='o')
            ax3.text(nnodes[idx]*1.1, efficiency[idx]+0.05, label, color=c)

# add axes grid
for ax in grid:
    ax.grid(axis='y')

# set scales
ax1.set_xscale('log')
ax1.set_yscale('log')
ax2.set_yscale('log')
ax1.set_xlim(1.0, 256)

# set axes labels
ax1.set_ylabel('real time (h)')
ax2.set_ylabel('speedup')
ax3.set_ylabel('efficiency')
ax3.set_xlabel('compute nodes (36 cores each)')
ax1.legend(loc='best')

# add ideal speedup curve
ax2.plot([1e0, 1e3], [1e0, 1e3], color='0.5')
angles = np.asarray([45])
points = np.asarray([[2e1, 2e1]])
angles = ax2.transData.transform_angles(angles, points)
ax2.text(points[0,0], points[0,1], 'ideal speedup', color='0.5',
         ha='center', va='bottom', rotation=angles[0])

# add subfigure labels
ut.pl.add_subfig_label('(a)', ax=ax1)
ut.pl.add_subfig_label('(b)', ax=ax2)
ut.pl.add_subfig_label('(c)', ax=ax3)

# save
fig.savefig('alpcyc_hr_scalability')
