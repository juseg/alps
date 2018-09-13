#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import xarray as xr
import multiprocessing as mp
import matplotlib.pyplot as plt
import util as ut

# crop region and language
crop = 'al'  # al ch lu
lang = 'en'  # de en fr

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

        # prepare axes coordinates
        x, y = ut.pl.coords_from_extent(ax.get_extent(),
                                        *fig.get_size_inches()*fig.dpi)

        # estimate sea level drop
        # FIXME preprocess or fix mfoutput ages, then remove xarray import
        with xr.open_dataset(os.environ['HOME']+'/pism/input/dsl/specmap.nc',
                             decode_times=False) as ds:
            dsl = ds.delta_SL.interp(time=t).data

        # load interpolated data
        filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
        with ut.io.load_visual(filepath, t, x, y) as ds:

            # plot basal topography
            ds.topg.plot.imshow(ax=ax, add_colorbar=False, cmap=ut.cm.topo,
                                vmin=dsl-3e3, vmax=dsl+3e3, zorder=-1)
            ds.topg.plot.contour(ax=ax, colors='#0978ab', levels=[dsl],
                                 linestyles=['dashed'], linewidths=0.25)

            # add relief shading
            ut.pl.draw_multishading(ds.topg, ax=ax)

            # plot surface topography
            ds.icy.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors='w',
                                 extend='neither', levels=[0.5, 1.5])
            ds.icy.plot.contour(ax=ax, colors=['0.25'], levels=[0.5],
                                linewidths=0.25)
            ds.usurf.plot.contour(ax=ax, colors=['0.25'], levels=ut.pl.inlevs,
                                  linewidths=0.1)
            ds.usurf.plot.contour(ax=ax, colors=['0.25'], levels=ut.pl.utlevs,
                                  linewidths=0.25)

        # load extra data
        with ut.io.load_mfoutput(filepath) as ds:

            # extract velocities
            ds = ds.sel(age=-t/1e3)
            x = ds.x
            y = ds.y
            u = ds.uvelsurf.where(ds.thk.fillna(0.0) >= 1.0).values
            v = ds.vvelsurf.where(ds.thk.fillna(0.0) >= 1.0).values
            c = (u**2+v**2)**0.5

            # try add streamplot (start point spacing 1.25 km == 1.5 px)
            try:
                ax.streamplot(x, y, u, v, cmap='Blues', color=c,
                              density=(24.0, 16.0), norm=ut.pl.velnorm,
                              linewidth=0.5, arrowsize=0.25)

            # handle lack of ice cover
            except ValueError:
                pass

        # draw map elements
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

        # language-dependent labels
        age_label = dict(en=r'{:,d} years ago',
                         fr=r'il y a {:,d} ans')[lang]
        tem_label = dict(en=u'temperature\nchange (°C)',
                         fr=u'écart (°C) de\ntempérature')[lang]
        vol_label = dict(en='ice volume\n(cm sea level)',
                         fr='vol. de glace\n(cm niv. marin)')[lang]

        # plot temperature offset time series
        with ut.io.load_postproc('alpcyc.1km.epic.pp.dt.nc') as ds:
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
        ax.set_ylabel(tem_label, color='0.25', labelpad=-1)
        ax.tick_params(axis='x', colors='0.25')
        ax.tick_params(axis='y', colors='0.25')

        # plot ice volume time series
        ax = ax.twinx()
        with ut.io.load_postproc('alpcyc.1km.epic.pp.ts.10a.nc') as ds:
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
        ax.set_ylabel(vol_label, color='C1')
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
