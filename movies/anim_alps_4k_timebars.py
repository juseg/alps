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
    ax.set_ylabel(label, color=color, labelpad=2, y=0.55)
    ax.tick_params(axis='y', colors=color)


def open_variable(var):
    """Open postprocessed time series from appropriate file."""
    filename = dict(
        dt='../data/processed/alpcyc.1km.epic.pp.dt.nc',
        er='../data/processed/alpero.1km.epic.pp.agg.nc',
        sl='../data/processed/alpcyc.1km.epic.pp.ts.10a.nc')[var]
    varname = dict(dt='delta_T', er='erosion_rate', sl='slvol')[var]
    multiplier = dict(dt=1.0, sl=100.0, er=1e-9)[var]
    with ut.open_dataset(filename) as ds:
        return ds[varname]*multiplier


def plot_cursor(ax, time, label, sep=r'$\,$'):
    """Add moving time cursor and adaptive ticks."""
    start, end = ax.get_xlim()
    ticks = [start, -time, end]
    labels = [r'{:,.0f}', label, '{:,.0f}']
    labels = [l.format(t).replace(',', sep) for l, t in zip(labels, ticks)]
    relpos = float((start+time)/(start-end))
    labels = [labels[0]*(relpos>=1/12), labels[1], labels[-1]*(relpos<=11/12)]
    ax.axvline(-time, c='0.25', lw=0.5)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.xaxis.tick_top()
    for label in ax.xaxis.get_ticklabels():
        label.set_verticalalignment('baseline')


def plot_tagline(ax, data, time, text='  {: .0f}', **kwargs):
    """Plot progress line with moving text time tag."""
    data = data[data.time <= time]
    ax.plot(data.age, data, **kwargs)
    ax.text(-time, data[-1], text.format(float(data[-1])),
            ha='left', va='center', clip_on=True, **kwargs)


def timebar(t, mode='co', lang='en', t0=-120000, t1=0):
    """Plot time bar overlay for given time."""

    # mode-dependent properties
    variables = dict(co=('dt', 'sl'), er=('sl', 'er'))[mode]
    colors = '0.25', dict(co='C0', er='C4')[mode]

    # initialize figure
    # FIXME use absplots
    figw, figh = 192.0, 20.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([12.0/figw, 3.0/figh, 1-26.0/figw, 12.0/figh])

    # import language-dependent labels
    # FIXME language-dependent erosion label
    with open('anim_alps_4k_zo_{}.yaml'.format(lang)) as f:
        age_label, tem_label, vol_label = yaml.safe_load(f)['Labels']

    # plot left axis variable
    data = open_variable(variables[0])
    plot_tagline(ax, data, t, color=colors[0])

    # color axes spines
    for k, v in ax.spines.items():
        v.set_color(colors[0] if k == 'left' else 'none')

    # add moving cursor and adaptive ticks
    ax.set_xlim(-t0, -t1)
    plot_cursor(ax, t, age_label, sep=(',' if lang == 'ja' else r'$\,$'))

    # set axes properties
    format_axes(ax, variables[0], color=colors[0], lang=lang)
    ax.tick_params(axis='x', colors=colors[0])

    # plot right axis variable
    ax = ax.twinx()
    data = open_variable(variables[1])
    if variables[1] != 'er':
        plot_tagline(ax, data, t, color=colors[1])
    else:
        roll = data.rolling(time=100, center=True).mean()
        plot_tagline(ax, data, t, text='', alpha=0.5, color=colors[1])
        plot_tagline(ax, roll, t, text='  {: .1f}', color=colors[1])

    # color axes spines
    for k, v in ax.spines.items():
        v.set_color(colors[1] if k == 'right' else 'none')

    # set axes properties
    format_axes(ax, variables[1], color=colors[1], lang=lang)

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
