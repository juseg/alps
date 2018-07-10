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
# FIXME this depends on crop region, suffix = '_%d%d' % (-t0/1e3, t1/1e3)
t0, t1, dt = -120000, -0, 40


def plot_main(t):
    """Plot main figure for given time."""

    # check if file exists
    fname = os.path.join(prefix+'_main_'+crop, '{:06d}.png'.format(t+120000))
    if not os.path.isfile(fname):

        # initialize figure
        print 'plotting {:s} ...'.format(fname)
        fig, ax = ut.pl.subplots_anim(figsize=(384.0, 216.0))

        # draw map elements
        ut.pl.draw_fancy_map(ax, t, density=(24.0, 13.5))
        ut.pl.draw_natural_earth_color(ax, graticules=False)

        # save
        fig.savefig(fname)
        plt.close(fig)


def plot_city():
    """Plot city overlay for given language."""

    # check if file exists
    fname = os.path.join(prefix+'_city_'+crop, lang+'.png')
    if not os.path.isfile(fname):

        # initialize figure
        print 'plotting {:s} ...'.format(fname)
        fig, ax = ut.pl.subplots_anim(figsize=(384.0, 216.0))

        # draw map elements
        ut.pl.draw_major_cities(ax, maxrank=8, lang=lang, request='Sion')

        # save
        fig.savefig(fname, facecolor='none')
        plt.close(fig)


def plot_tbar(t):
    """Plot time bar overlay for given time."""

    # check if file exists
    fname = os.path.join(prefix+'_tbar_'+lang, '{:06d}.png').format(t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print 'plotting {:s} ...'.format(fname)
        figw, figh = 192.0, 20.0
        fig = plt.figure(figsize=(figw/25.4, figh/25.4))
        ax = fig.add_axes([12.0/figw, 3.0/figh, 1-24.0/figw, 12.0/figh])
        ax.set_facecolor('none')

        # plot time series
        ut.pl.plot_dt_fancy(ax, t, t0, t1, lang=lang)
        ut.pl.plot_slvol_fancy(ax.twinx(), t, lang=lang)

        # save
        fig.savefig(fname, dpi=508.0, facecolor='none')
        plt.close(fig)


def plot_ttag(t):
    """Plot time tag overlay for given time."""

    # check if file exists
    fname = os.path.join(prefix+'_ttag_'+lang, '{:06d}.png').format(t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print 'plotting {:s} ...'.format(fname)
        figw, figh = 32.0, 6.0
        fig = plt.figure(figsize=(figw/25.4, figh/25.4))

        # add text
        tag = dict(de=u'{:d} Jahre früher',
                   en=u'{:d} years ago',
                   fr=u'il y a {:d} ans')[lang]
        fig.text(2.5/figw, 1-2.5/figh, tag.format(0-t),
                 ha='left', va='top', fontweight='bold')

        # save
        fig.savefig(fname, dpi=508.0, facecolor='none')
        plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frame directories if missing
    for suffix in ['_main_'+crop, '_city_'+crop, '_ttag_'+lang, '_tbar_'+lang]:
        if not os.path.isdir(prefix + suffix):
            os.mkdir(prefix + suffix)

    # plot all frames in parallel
    pool = mp.Pool(processes=4)
    pool.map(plot_main, xrange(t0+dt, t1+1, dt))
    pool.map(plot_tbar, xrange(t0+dt, t1+1, dt))
    pool.map(plot_ttag, xrange(t0+dt, t1+1, dt))
    pool.apply(plot_city)
    pool.close()
    pool.join()
