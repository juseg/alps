#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import multiprocessing as mp
import matplotlib.pyplot as plt

# animation language
lang = 'fr'

# frames output directory
videoname = os.path.basename(os.path.splitext(sys.argv[0])[0])
videoname += (lang != 'en') * ('_'+lang)
framesdir = os.path.join(os.environ['HOME'], 'anim', videoname)

# start and end of animation
t0, t1, dt = -120000, 0, 40


def draw(t):
    """Plot complete figure for given time."""

    # check if file exists
    framepath = os.path.join(framesdir, '{:06d}.png'.format(t+120000))
    if os.path.isfile(framepath):
        return

    # initialize figure
    print 'plotting at %.0f a...' % (0.0-t)
    fig, ax, tsax = ut.pl.subplots_fancy(t=t)
    ut.pl.set_dynamic_extent(ax, t, 'swiss0', '1609', t0, t1)

    # draw map elements
    ut.pl.draw_fancy_map(ax, t)
    ut.pl.draw_natural_earth_color(ax)
    ut.pl.draw_major_cities(ax, maxrank=6, lang=lang, request='Sion')

    # plot time series
    ut.pl.plot_dt_fancy(tsax, t, t0, t1, lang=lang)
    ut.pl.plot_slvol_fancy(tsax.twinx(), t, lang=lang)

    # save
    fig.savefig(framepath)
    plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frames directory if missing
    if not os.path.isdir(framesdir):
        os.mkdir(framesdir)

    # plot all frames in parallel
    pool = mp.Pool(processes=12)
    pool.map(draw, xrange(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
