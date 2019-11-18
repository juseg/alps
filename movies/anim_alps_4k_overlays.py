#!/usr/bin/env python
# Copyright (c) 2018-2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import os
import yaml
import multiprocessing as mp
import matplotlib.pyplot as plt
import utils as ut

# FIXME Split this into one script per overlay, or consider a tbar mode
# FIXME Each tbar variable has a color, yticks, and label.


def overlay_ebar(t, lang='en', t0=-120e3, t1=0e3):
    """Plot erosion time bar overlay for given time."""

    # initialize figure
    figw, figh = 192.0, 20.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([12.0/figw, 3.0/figh, 1-26.0/figw, 12.0/figh])

    # import language-dependent labels
    # FIXME language-dependent erosion label
    with open('anim_alps_4k_zo_{}.yaml'.format(lang)) as f:
        age_label, tem_label, vol_label = yaml.safe_load(f)['Labels']

    # plot temperature offset time series
    with ut.open_dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
        sl = ds.slvol[ds.time <= t]*100.0
        ax.plot(sl.age, sl, c='0.25')
        ax.text(-t, sl[-1], '  {: .0f}'.format(sl[-1].values),
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
    ax.set_ylim(-5, 35)
    ax.set_yticks([0, 30])
    ax.set_ylabel(vol_label, color='0.25', labelpad=-1, y=0.55)
    ax.tick_params(axis='x', colors='0.25')
    ax.tick_params(axis='y', colors='0.25')

    # plot volumic erosion rate time series
    ax = ax.twinx()
    with ut.open_dataset('../data/processed/alpero.1km.epic.pp.agg.nc') as ds:
        eros = ds.erosion_rate[ds.time <= t]*1e-9
        roll = eros.rolling(time=100, center=True).mean()
        last = float(roll.dropna(dim='time')[-1])
        ax.plot(eros.age, eros, c='C4', alpha=0.5)
        ax.plot(roll.age, roll, c='C4')
        ax.text(-t, last, '  {: .1f}'.format(last),
                color='C4', ha='left', va='center', clip_on=True)

    # color axes spines
    for k, v in ax.spines.items():
        v.set_color('C4' if k == 'right' else 'none')

    # set axes properties
    # FIXME language-dependent erosion label
    ax.set_xlim(-t0, -t1)
    ax.set_ylim(-0.25, 1.75)
    ax.set_yticks([0.0, 1.5])
    ax.set_ylabel('erosion rate\n'+r'($km\,a^{-1}$)', color='C4', y=0.55)
    ax.tick_params(axis='y', colors='C4')

    # return figure
    return fig


def overlay_tbar(t, lang='en', t0=-120e3, t1=0e3):
    """Plot time bar overlay for given time."""

    # initialize figure
    figw, figh = 192.0, 20.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([12.0/figw, 3.0/figh, 1-26.0/figw, 12.0/figh])

    # import language-dependent labels
    with open('anim_alps_4k_zo_{}.yaml'.format(lang)) as f:
        age_label, tem_label, vol_label = yaml.safe_load(f)['Labels']

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


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'zo'])
    parser.add_argument('lang', choices=['de', 'en', 'fr', 'it', 'ja', 'nl'])
    args = parser.parse_args()

    # set default font properties
    plt.rc('savefig', dpi=508, facecolor='none')
    plt.rc('axes', facecolor='none')
    if args.lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # start and end of animation
    if args.crop in ('lu', 'ma'):
        t0, t1, dt = -45000, -15000, 10
    else:
        t0, t1, dt = -120000, -0, 10000

    # output frame directories
    prefix = os.path.join(os.environ['HOME'], 'anim', 'anim_alps_4k')
    suffix = '{:.0f}{:.0f}'.format(-t0/1e3, -t1/1e3)
    ebar_dir = prefix + '_ebar_' + args.lang + '_' + suffix
    tbar_dir = prefix + '_tbar_' + args.lang + '_' + suffix

    # range of frames to save
    time_range = range(t0+dt, t1+1, dt)

    # iterable arguments to save animation frames
    ebar_args = [(overlay_ebar, ebar_dir, t, args.lang, t0, t1)
                 for t in time_range]
    tbar_args = [(overlay_tbar, tbar_dir, t, args.lang, t0, t1)
                 for t in time_range]

    # create frame directories if missing
    for outdir in [ebar_dir, tbar_dir]:
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, ebar_args+tbar_args)


if __name__ == '__main__':
    main()
