#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import multiprocessing as mp
import matplotlib.pyplot as plt


def draw(t):
    """Plot complete figure for given time."""

    # initialize figure
    fig, ax, tsax = ut.pl.subplots_fancy(t=t)
    ut.pl.add_signature(u'J. Seguinot (2018)')

    # set dynamics axes extent
    a0 = 40e3  # age of animation start
    a1 = 15e3  # age of animation end
    zf = 1 - ((t+a1)/(a0-a1))**2  # zoom factor between 0 and 1
    e0 = 415e3, 505e3, 5195e3, 5255e3  # Luzern 90x60 km
    e1 = 400e3, 520e3, 5190e3, 5270e3  # Luzern 120x80 km
    axe = [c0 + (c1-c0)*zf for (c0, c1) in zip(e0, e1)]
    ax.set_extent(axe, crs=ax.projection)

    # plot model results
    ut.pl.draw_fancy_map(ax, t=t)

    ## add colorbar
    #cb = ut.pl.add_colorbar(ss.lines, cax, extend='both', format='%g')
    #cb.set_label(r'surface velocity ($m\,a^{-1}$)')
    #cb.set_ticks([1e1, 1e2, 1e3])

    # add vectors
    ut.pl.draw_swisstopo_hydrology(ax)
    ut.pl.draw_major_cities(ax, maxrank=8)
    ut.pl.add_corner_tag('%.0f years ago' % (0.0-t), ax)

    # plot time series
    ut.pl.plot_dt_fancy(tsax, t=t)
    ut.pl.plot_slvol_fancy(tsax.twinx(), t=t)
    tsax.set_xlim(a0/1e3, a1/1e3)
    tsax.set_xticks(tsax.get_xlim())

    # return figure
    return fig


def saveframe(years):
    """Independently plot one frame."""

    # check if file exists
    videoname = os.path.splitext(sys.argv[0])[0]
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
    dt = 10
    pool = mp.Pool(processes=12)
    pool.map(saveframe, xrange(80000, 105001, dt))
    pool.join()
