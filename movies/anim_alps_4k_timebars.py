#!/usr/bin/env python
# Copyright (c) 2018-2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import os
import yaml
import multiprocessing as mp
import matplotlib.pyplot as plt
import utils as ut

"""Plot Alps 4k animations time bar overlays."""

def format_axes(ax, var, color='0.25', lang='en'):
    """Format axes for given variable."""

    # import language-dependent labels
    # FIXME language-dependent erosion label
    with open('anim_alps_4k_zo_{}.yaml'.format(lang)) as f:
        age_label, tem_label, vol_label = yaml.safe_load(f)['Labels']

    # get axes properties
    label = dict(dt=tem_label, sl=vol_label, er='erosion rate\n($km\,a^{-1}$)')[var]
    ticks = dict(dt=[-15, 0], sl=[0, 30], er=[0, 1.5])[var]
    ylims = ticks[0]-(ticks[1]-ticks[0])/6, ticks[1]+(ticks[1]-ticks[0])/6

    # set axes properties
    ax.set_yticks(ticks)
    ax.set_ylim(*ylims)
    ax.set_ylabel(label, color=color, labelpad=-1, y=0.55)
    ax.tick_params(axis='y', colors=color)


def plot_tagline(ax, data, text='  {: .0f}', **kwargs):
    """Plot progress line with moving text time tag."""
    # FIXME age coord of dt file not exactly at cursor, is it an issue?
    ax.plot(data.age, data, **kwargs)
    ax.text(data.age[-1], data[-1], text.format(float(data[-1])),
            ha='left', va='center', clip_on=True, **kwargs)


def timebar(t, mode='co', lang='en', t0=-120000, t1=0):
    """Plot time bar overlay for given time."""

    # initialize figure
    figw, figh = 192.0, 20.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([12.0/figw, 3.0/figh, 1-26.0/figw, 12.0/figh])

    # import language-dependent labels
    # FIXME language-dependent erosion label
    with open('anim_alps_4k_zo_{}.yaml'.format(lang)) as f:
        age_label, tem_label, vol_label = yaml.safe_load(f)['Labels']

    # plot left axis variable
    if mode == 'co':
        with ut.open_dataset('../data/processed/alpcyc.1km.epic.pp.dt.nc') as ds:
            data = ds.delta_T[ds.time <= t]
            plot_tagline(ax, data, color='0.25')
    elif mode == 'er':
        with ut.open_dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
            data = ds.slvol[ds.time <= t]*100.0
            plot_tagline(ax, data, color='0.25')

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
    if mode == 'co':
        format_axes(ax, 'dt', color='0.25', lang=lang)
    elif mode == 'er':
        format_axes(ax, 'sl', color='0.25', lang=lang)
    ax.tick_params(axis='x', colors='0.25')

    # plot right axis variable
    ax = ax.twinx()
    if mode == 'co':
        with ut.open_dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
            data = ds.slvol[ds.time <= t]*100.0
            plot_tagline(ax, data, color='C0')
    elif mode == 'er':
        with ut.open_dataset('../data/processed/alpero.1km.epic.pp.agg.nc') as ds:
            data = ds.erosion_rate[ds.time <= t]*1e-9
            roll = ds.erosion_rate.rolling(time=100, center=True).mean()[ds.time <= t]*1e-9
            plot_tagline(ax, data, text='', alpha=0.5, color='C4')
            plot_tagline(ax, roll, text='  {: .1f}', color='C4')

    # color axes spines
    for k, v in ax.spines.items():
        if mode == 'co':
            v.set_color('C0' if k == 'right' else 'none')
        elif mode == 'er':
            v.set_color('C4' if k == 'right' else 'none')

    # set axes properties
    ax.set_xlim(-t0, -t1)
    if mode == 'co':
        format_axes(ax, 'sl', color='C0', lang=lang)
    elif mode == 'er':
        format_axes(ax, 'er', color='C4', lang=lang)

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'zo'])
    parser.add_argument('mode', choices=['co', 'er'])
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

    # output frames directory
    outdir = os.path.join(
        os.environ['HOME'], 'anim', 'anim_alps_4k_tbar_{}_{}_{:.0f}{:.0f}'.format(
            args.mode, args.lang, -t0/1e3, -t1/1e3))

    # iterable arguments to save animation frames
    iter_args = [(timebar, outdir, t, args.mode, args.lang, t0, t1)
                 for t in range(t0+dt, t1+1, dt)]

    # create frames directory if missing
    if not os.path.isdir(outdir):
         os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
