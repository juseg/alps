#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import multiprocessing as mp
import matplotlib.pyplot as plt

# frames output directory
videoname = os.path.basename(os.path.splitext(sys.argv[0])[0])
framesdir = os.path.join(os.environ['HOME'], 'anim', videoname)

# start and end of animation
t0, t1, dt = -45000, -15000, 10


def draw(t):
    """Plot complete figure for given time."""

    # check if file exists
    framepath = os.path.join(framesdir, '{:06d}.png'.format(t+120000))
    if os.path.isfile(framepath):
        return

    # initialize figure
    print 'plotting at %.0f a...' % (0.0-t)
    fig, ax, tsax = ut.pl.subplots_fancy(t=t)
    ut.pl.set_dynamic_extent(ax, t, 'reuss0', 'reuss1', t0, t1)

    # draw map elements
    ut.pl.draw_fancy_map(ax, t)
    ut.pl.draw_swisstopo_hydrology(ax)
    ut.pl.draw_major_cities(ax, maxrank=8)

    # plot time series
    ut.pl.plot_dt_fancy(tsax, t, t0, t1)
    ut.pl.plot_slvol_fancy(tsax.twinx(), t)

    # save
    fig.savefig(framepath)
    plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frames directory if missing
    videoname = os.path.basename(os.path.splitext(sys.argv[0])[0])
    framesdir = os.path.join(os.environ['HOME'], 'anim', videoname)
    if not os.path.isdir(framesdir):
        os.mkdir(framesdir)

    # plot all frames in parallel
    pool = mp.Pool(processes=12)
    pool.map(draw, xrange(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
