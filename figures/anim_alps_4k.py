#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import multiprocessing as mp
import matplotlib.pyplot as plt

# crop region and language
crop='al'  # al ch lu
lang='en'  # de en fr

# prefix for output files
prefix = os.path.basename(os.path.splitext(sys.argv[0])[0])
prefix = os.path.join(os.environ['HOME'], 'anim', prefix)

# start and end of animation
# FIXME this depends on crop region
t0, t1, dt = -120000, -0, 40


def plot_main(t):
    """Plot main figure for given time."""

    # check if file exists
    of = os.path.join('{:s}_{:s}', '{:06d}.png').format(prefix, crop, t+120000)
    if not os.path.isfile(of):

        # initialize figure
        print 'plotting {:s} ...'.format(of)
        fig, ax = ut.pl.subplots_anim(figsize=(384.0, 216.0))

        # draw map elements
        ut.pl.draw_fancy_map(ax, t, density=(24.0, 13.5))
        ut.pl.draw_natural_earth_color(ax, graticules=False)

        # save
        fig.savefig(of)
        plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frames directory if missing
    if not os.path.isdir(prefix + '_' + crop):
        os.mkdir(prefix + '_' + crop)

    # plot all frames in parallel
    pool = mp.Pool(processes=4)
    pool.map(plot_main, xrange(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
