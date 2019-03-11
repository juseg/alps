#!/usr/bin/env python
# coding: utf-8

import os
import yaml
import multiprocessing as mp
import matplotlib.pyplot as plt
import utils as ut


def overlay_city(t, crop='al', lang='en', t0=-120e3, t1=0e3):
    """Plot city overlay for given language."""

    # initialize figure
    fig, ax = ut.axes_anim_dynamic(crop=crop, t=t, t0=t0, t1=t1,
                                   figsize=(192.0, 108.0))

    # draw map elements
    ut.draw_major_cities(ax=ax, exclude='Monaco', include='Sion', lang=lang,
                         maxrank=(8 if crop in ('lu', 'ma') else 6))

    # return figure
    return fig


def overlay_tbar(t, lang='en', t0=-120e3, t1=0e3):
    """Plot time bar overlay for given time."""

    # initialize figure
    figw, figh = 192.0, 20.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([12.0/figw, 3.0/figh, 1-26.0/figw, 12.0/figh])

    # import language-dependent labels
    with open('anim_alps_4k_al_{}.yaml'.format(lang)) as f:
        age_label, tem_label, vol_label = yaml.load(f)['Labels']

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

    # return figure
    return fig


def overlay_ttag(t, lang='en'):
    """Plot time tag overlay for given time."""

    # initialize figure
    figw, figh = 32.0, 6.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))

    # import language-dependent label
    with open('anim_alps_4k_al_{}.yaml'.format(lang)) as f:
        tag = yaml.load(f)['Labels'][0].format(0-t)
    if lang != 'ja':
        tag = tag.replace(',', r'$\,$')
    fig.text(2.5/figw, 1-2.5/figh, tag, ha='left', va='top', fontweight='bold')

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'zo'])
    parser.add_argument('lang', choices=['de', 'en', 'fr', 'it', 'ja', 'nl'])
    args = parser.parse_args()

    # set default font properties
    plt.rc('savefig', dpi=508, facecolor='none')
    plt.rc('axes', facecolor='none')
    if args.lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # start and end of animation
    if args.crop == 'lu':
        t0, t1, dt = -45000, -15000, 10
    else:
        t0, t1, dt = -120000, -0, 40

    # output frame directories
    prefix = os.path.join(os.environ['HOME'], 'anim', 'anim_alps_4k')
    suffix = '{:.0f}{:.0f}'.format(-t0/1e3, -t1/1e3)
    city_dir = prefix + '_city_' + args.crop + '_' + args.lang
    tbar_dir = prefix + '_tbar_' + args.lang + '_' + suffix
    ttag_dir = prefix + '_ttag_' + args.lang + '_' + suffix

    # range of frames to save
    time_range = range(t0+dt, t1+1, dt)
    city_range = [t1] if args.crop == 'al' else time_range

    # iterable arguments to save animation frames
    city_args = [(overlay_city, city_dir, t, args.crop, args.lang, t0, t1)
                 for t in city_range]
    tbar_args = [(overlay_tbar, tbar_dir, t, args.lang, t0, t1)
                 for t in time_range]
    ttag_args = [(overlay_ttag, ttag_dir, t, args.lang)
                 for t in time_range]

    # create frame directories if missing
    for outdir in [city_dir, tbar_dir, ttag_dir]:
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, city_args+tbar_args+ttag_args)


if __name__ == '__main__':
    main()
