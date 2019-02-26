#!/usr/bin/env python
# coding: utf-8

import os
import multiprocessing as mp
import matplotlib.pyplot as plt
import utils as ut


def overlay_city(prefix, crop, lang, t, t0=-120e3, t1=0e3):
    """Plot city overlay for given language."""

    # check if file exists
    fname = '{}_city_{}_{}/{:06d}.png'.format(prefix, crop, lang, t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print('plotting {:s} ...'.format(fname))
        fig, ax = ut.subplots_anim_dynamic(crop, t=t, t0=t0, t1=t1,
                                           figsize=(192.0, 108.0))

        # draw map elements
        ut.draw_major_cities(ax, exclude='Monaco', include='Sion',
                             maxrank=6, lang=lang)

        # save
        fig.savefig(fname, dpi=508, facecolor='none')
        plt.close(fig)


def overlay_tbar(prefix, lang, t, t0=-120e3, t1=0e3):
    """Plot time bar overlay for given time."""

    # check if file exists
    fname = os.path.join(prefix+'_tbar_'+lang, '{:06d}.png').format(t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print('plotting {:s} ...'.format(fname))
        figw, figh = 192.0, 20.0
        fig = plt.figure(figsize=(figw/25.4, figh/25.4))
        ax = fig.add_axes([12.0/figw, 3.0/figh, 1-26.0/figw, 12.0/figh])
        ax.set_facecolor('none')

        # language-dependent labels
        age_label = dict(de=u'{:,d} Jahre früher',
                         en=u'{:,d} years ago',
                         fr=u'il y a {:,d} ans',
                         it=u'{:,d} anni fa',
                         ja=u'{:,d}年前',
                         nl=u'{:,d} jaar geleden')[lang]
        tem_label = dict(de=u'Temperatur-\nänderung (°C)',
                         en=u'temperature\nchange (°C)',
                         fr=u'écart (°C) de\ntempérature',
                         it=u'variazione (°C)\ndi temperatura',
                         ja=u'現在との気温差\n（度）',
                         nl=u'temperatuur\nverandering (°C)')[lang]
        vol_label = dict(de=u'Eisvolumen\n(cm Meeresspiegel\näquivalent)',
                         en=u'ice volume\n(cm sea level\nequivalent)',
                         fr=u'volume de glace\n(cm équivalent\nniveau des mers)',
                         it=u'vol. del ghiaccio\n(equiv. a livello\ndel mare in cm)',
                         ja=u'氷体積の\n海水準相当量\n（センチメートル）',
                         nl=u'ijs volume\n(cm zee spiegel\nequivalent)')[lang]

        # plot temperature offset time series
        with ut.open_dataset('../data/processed/alpcyc.1km.epic.pp.dt.nc') as ds:
            dt = ds.delta_T[ds.time <= t]
            ax.plot(dt.age, dt, c='0.25')
            ax.text(-t, dt[-1], '  {: .0f}'.format(dt[-1].values),
                    color='0.25', ha='left', va='center', clip_on=True)

        # color axes spines
        for k, v in ax.spines.items():
            v.set_color('0.25' if k == 'left' else 'none')

        # add moving cursor and adaptive ticks
        ax.axvline(-t, c='0.25', lw=0.5)
        ax.set_xticks([-t0, -t, -t1])
        rt = 1.0*(t-t0)/(t1-t0)  # relative cursor position
        l0 = r'{:,d}'.format(0-t0)
        lt = age_label.format(0-t)
        l1 = r'{:,d}'.format(0-t1)
        if lang != 'ja':
            l0 = l0.replace(',', r'$\,$')
            lt = lt.replace(',', r'$\,$')
            l1 = l1.replace(',', r'$\,$')
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
        with ut.open_dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
            sl = ds.slvol[ds.time <= t]*100.0
            ax.plot(sl.age, sl, c='C0')
            ax.text(-t, sl[-1], '  {: .0f}'.format(sl[-1].values),
                    color='C0', ha='left', va='center', clip_on=True)

        # color axes spines
        for k, v in ax.spines.items():
            v.set_color('C0' if k == 'right' else 'none')

        # set axes properties
        ax.set_xlim(-t0, -t1)
        ax.set_ylim(-5.0, 35.0)
        ax.set_yticks([0.0, 30.0])
        ax.set_ylabel(vol_label, color='C0', y=0.55)
        ax.tick_params(axis='y', colors='C0')

        # save
        fig.savefig(fname, dpi=508.0, facecolor='none')
        plt.close(fig)


def overlay_ttag(prefix, lang, t):
    """Plot time tag overlay for given time."""

    # check if file exists
    fname = os.path.join(prefix+'_ttag_'+lang, '{:06d}.png').format(t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print('plotting {:s} ...'.format(fname))
        figw, figh = 32.0, 6.0
        fig = plt.figure(figsize=(figw/25.4, figh/25.4))

        # add text
        tag = dict(de=u'{:,d} Jahre früher',
                   en=u'{:,d} years ago',
                   fr=u'il y a {:,d} ans',
                   it=u'{:,d} anni fa',
                   ja=u'{:,d}年前',
                   nl=u'{:,d} jaar geleden')[lang]
        tag = tag.format(0-t)
        if lang != 'ja':
            tag = tag.replace(',', r'$\,$')
        fig.text(2.5/figw, 1-2.5/figh, tag,
                 ha='left', va='top', fontweight='bold')

        # save
        fig.savefig(fname, dpi=508.0, facecolor='none')
        plt.close(fig)


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', help='crop region',
                        choices=['al', 'ch', 'lu', 'zo'])
    parser.add_argument('lang', help='anim language',
                        choices=['de', 'en', 'fr', 'it', 'ja', 'nl'])
    args = parser.parse_args()

    # set default font properties
    plt.rc('figure', dpi=508, facecolor='none')

    # japanese input font
    if args.lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # start and end of animation
    # FIXME this depends on crop region, suffix = '_%d%d' % (-t0/1e3, t1/1e3)
    t0, t1, dt = -120000, -0, 40000

#    # import text elements
#    with open(prefix+'.yaml') as f:
#        info = yaml.load(f)

    # prefix for output files
    prefix = 'anim_alps_4k'.format(args.crop, args.lang)
    prefix = os.path.join(os.environ['HOME'], 'anim', prefix)

    # create frame directories if missing
    for suffix in ['_city_' + args.crop + '_' + args.lang,
                   '_ttag_' + args.lang,
                   '_tbar_' + args.lang]:
        if not os.path.isdir(prefix + suffix):
            os.mkdir(prefix + suffix)

    # plot all frames in parallel
    times = range(t0+dt, t1+1, dt)
    with mp.Pool(processes=4) as pool:
        pool.starmap(overlay_city, [(prefix, args.crop, args.lang, t, t0, t1) for t in times])
        pool.starmap(overlay_tbar, [(prefix, args.lang, t, t0, t1) for t in times])
        pool.starmap(overlay_ttag, [(prefix, args.lang, t) for t in times])


if __name__ == '__main__':
    main()
