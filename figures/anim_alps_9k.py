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
t0, t1, dt = -120000, 0, 5000


def draw(t):
    """Plot complete figure for given time."""

    # check if file exists
    framepath = os.path.join(framesdir, '{:06d}.png'.format(t+120000))
    if not os.path.isfile(framepath):

        # initialize figure
        print 'plotting at %.0f a...' % (0.0-t)
        fig, ax = ut.pl.subplots_anim(extent='alps', figsize=(900.0, 600.0))

        # plot model results
        ut.pl.draw_fancy_map(ax, t, density=(60, 40), bg=False)

        # save
        fig.savefig(framepath, facecolor='none')
        plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frames directory if missing
    if not os.path.isdir(framesdir):
        os.mkdir(framesdir)

    # plot all frames in parallel
    pool = mp.Pool(processes=4)
    pool.map(draw, xrange(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
