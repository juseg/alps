#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import multiprocessing as mp
import matplotlib.pyplot as plt


# start and end of animation
t0, t1 = -45e3, -15e3

def draw(t):
    """Plot complete figure for given time."""

    # initialize figure
    fig, ax, tsax = ut.pl.subplots_fancy(t=t)
    ut.pl.set_dynamic_extent(ax, t, 'reuss0', 'reuss1', t0, t1)

    # draw map elements
    ut.pl.draw_fancy_map(ax, t)
    ut.pl.draw_swisstopo_hydrology(ax)
    ut.pl.draw_major_cities(ax, maxrank=8)

    # plot time series
    ut.pl.plot_dt_fancy(tsax, t, t0, t1)
    ut.pl.plot_slvol_fancy(tsax.twinx(), t)

    # return figure
    return fig


def saveframe(years):
    """Independently plot one frame."""

    # check if file exists
    videoname = os.path.basename(os.path.splitext(sys.argv[0])[0])
    framesdir = os.path.join(os.environ['HOME'], 'anim', videoname)
    framepath = os.path.join(framesdir, '{:06d}.png'.format(years))
    if os.path.isfile(framepath):
        return

    # create tmp directory if missing
    if not os.path.exists(framesdir):
        os.makedirs(framesdir)

    # plot
    t = years - 120e3
    print 'plotting at %.0f a...' % (0.0-t)
    fig = draw(t)

    # save
    fig.savefig(framepath)
    plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""
    y0 = int(round(120e3+t0))
    y1 = int(round(120e3+t1))
    dy = 10
    pool = mp.Pool(processes=12)
    pool.map(saveframe, xrange(y0, y1+1, dy))
    pool.close()
    pool.join()
