#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import xarray as xr
import multiprocessing as mp
import matplotlib.pyplot as plt
import util as ut

# crop region and language
crop = 'zo'  # al ch lu zo
lang = 'en'  # de en fr

# prefix for output files
prefix = os.path.basename(os.path.splitext(sys.argv[0])[0])
prefix = os.path.join(os.environ['HOME'], 'anim', prefix)

# start and end of animation
# FIXME this depends on crop region, suffix = '_%d%d' % (-t0/1e3, t1/1e3)
t0, t1, dt = -120000, -0, 10000


def plot_main(t):
    """Plot main figure for given time."""

    # check if file exists
    fname = '{}_main_{}/{:06d}.png'.format(prefix, crop, t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print 'plotting {:s} ...'.format(fname)
        fig, ax = ut.fi.subplots_anim_dynamic(crop, t=t, t0=t0, t1=t1,
                                              figsize=(384.0, 216.0))

        # prepare axes coordinates
        x, y = ut.pl.coords_from_extent(ax.get_extent(),
                                        *fig.get_size_inches()*fig.dpi)

        # estimate sea level drop
        dsl = ut.io.open_sealevel(t)

        # plot interpolated data
        filename = '~/pism/' + ut.alpcyc_bestrun + 'y{:07.0f}-extra.nc'
        with ut.io.open_visual(filename, t, x, y) as ds:
            ut.xp.shaded_relief(ds.topg-dsl, ax=ax)
            ut.xp.ice_extent(ds.icy, ax=ax, fc='w')
            ut.xp.topo_contours(ds.usurf, ax=ax)

        # plot extra data
        with ut.io.open_subdataset(filename, t) as ds:
            ut.xp.streamplot(ds, ax=ax, density=(24, 16))

        # draw map elements
        ut.pl.draw_natural_earth_color(ax, graticules=False)

        # save
        fig.savefig(fname)
        plt.close(fig)


def plot_city(t):
    """Plot city overlay for given language."""

    # check if file exists
    fname = '{}_city_{}_{}/{:06d}.png'.format(prefix, crop, lang, t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print 'plotting {:s} ...'.format(fname)
        fig, ax = ut.fi.subplots_anim_dynamic(crop, t=t, t0=t0, t1=t1,
                                              figsize=(384.0, 216.0))

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

        # language-dependent labels
        age_label = dict(de=u'{:,d} Jahre früher',
                         en=u'{:,d} years ago',
                         fr=u'il y a {:,d} ans')[lang]
        tem_label = dict(de=u'Temperatur-\nänderung (°C)',
                         en=u'temperature\nchange (°C)',
                         fr=u'écart (°C) de\ntempérature')[lang]
        vol_label = dict(de=u'Eisvolumen\n(cm Meereshöhe)',
                         en=u'ice volume\n(cm sea level)',
                         fr=u'volume de glace\n(cm niveau mers)')[lang]

        # plot temperature offset time series
        with ut.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.dt.nc') as ds:
            dt = ds.delta_T[ds.age >= -t]
            ax.plot(dt.age, dt, c='0.25')
            ax.text(-t, dt[-1], '  {: .0f}'.format(dt[-1].values),
                    color='0.25', ha='left', va='center', clip_on=True)

        # color axes spines
        for k, v in ax.spines.iteritems():
            v.set_color('0.25' if k == 'left' else 'none')

        # add moving cursor and adaptive ticks
        ax.axvline(-t, c='0.25', lw=0.5)
        ax.set_xticks([-t0, -t, -t1])
        rt = 1.0*(t-t0)/(t1-t0)  # relative cursor position
        l0 = r'{:,d}'.format(0-t0).replace(',', r'$\,$')
        lt = age_label.format(0-t).replace(',', r'$\,$')
        l1 = r'{:,d}'.format(0-t1).replace(',', r'$\,$')
        ax.set_xticklabels([l0*(rt>=1/12.0), lt, l1*(rt<=11/12.0)])
        ax.xaxis.tick_top()

        # set axes properties
        ax.set_ylim(-17.5, 2.5)
        ax.set_yticks([-15.0, 0.0])
        ax.set_ylabel(tem_label, color='0.25', labelpad=-1, y=0.55)
        ax.tick_params(axis='x', colors='0.25')
        ax.tick_params(axis='y', colors='0.25')

        # plot ice volume time series
        ax = ax.twinx()
        with ut.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
            sl = ds.slvol[ds.age >= -t]*100.0
            ax.plot(sl.age, sl, c='C1')
            ax.text(-t, sl[-1], '  {: .0f}'.format(sl[-1].values),
                    color='C1', ha='left', va='center', clip_on=True)

        # color axes spines
        for k, v in ax.spines.iteritems():
            v.set_color('C1' if k == 'right' else 'none')

        # set axes properties
        ax.set_xlim(-t0, -t1)
        ax.set_ylim(-5.0, 35.0)
        ax.set_yticks([0.0, 30.0])
        ax.set_ylabel(vol_label, color='C1', y=0.55)
        ax.tick_params(axis='y', colors='C1')

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
        tag = dict(de=u'{:,d} Jahre früher',
                   en=u'{:,d} years ago',
                   fr=u'il y a {:,d} ans')[lang]
        fig.text(2.5/figw, 1-2.5/figh, tag.format(0-t).replace(',', r'$\,$'),
                 ha='left', va='top', fontweight='bold')

        # save
        fig.savefig(fname, dpi=508.0, facecolor='none')
        plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frame directories if missing
    for suffix in ['_main_'+crop, '_city_'+crop+'_'+lang,
                   '_ttag_'+lang, '_tbar_'+lang]:
        if not os.path.isdir(prefix + suffix):
            os.mkdir(prefix + suffix)

    # plot all frames in parallel
    pool = mp.Pool(processes=4)
    pool.map(plot_main, xrange(t0+dt, t1+1, dt))
    pool.map(plot_city, xrange(t0+dt, t1+1, dt))
    pool.map(plot_tbar, xrange(t0+dt, t1+1, dt))
    pool.map(plot_ttag, xrange(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
