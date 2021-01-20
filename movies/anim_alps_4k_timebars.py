#!/usr/bin/env python
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps 4k animations time bar overlays."""

import os.path
import argparse
import multiprocessing as mp
import yaml
import matplotlib.pyplot as plt
import absplots as apl
import pismx.open
import utils as ut


def format_axes(ax, var, color='0.25', label=''):
    """Format axes for given variable."""

    # get axes properties
    ticks = dict(dt=[-15, 0], sl=[0, 30], er=[0, 6], ul=[-30, 0])[var]
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
        sl='../data/processed/alpcyc.1km.epic.pp.ts.10a.nc',
        ul='../data/processed/alpero.1km.epic.pp.agg.nc')[var]
    varname = dict(dt='delta_T', er='kop2015_rate', sl='slvol',
                   ul='volumic_lift')[var]
    multiplier = dict(dt=1.0, sl=100.0, er=1e-6, ul=1e-12)[var]
    with pismx.open.dataset(filename) as ds:
        return ds[varname]*multiplier


def plot_cursor(ax, time, label, color='0.25', sep=r'$\,$'):
    """Add moving time cursor and adaptive ticks."""
    start, end = ax.get_xlim()
    ticks = [start, -time, end]
    labels = [r'{:,.0f}', label, '{:,.0f}']
    labels = [lab.format(t).replace(',', sep) for lab, t in zip(labels, ticks)]
    relpos = float((start+time)/(start-end))
    labels = [labels[0]*(relpos >= 1/12),
              labels[1],
              labels[-1]*(relpos <= 11/12)]
    ax.axvline(-time, c='0.25', lw=0.5)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.tick_params(axis='x', colors=color)
    ax.xaxis.tick_top()
    for lab in ax.xaxis.get_ticklabels():
        lab.set_verticalalignment('baseline')


def plot_tagline(ax, data, time, text='  {: .0f}', **kwargs):
    """Plot progress line with moving text time tag."""
    data = data[data.age >= -time/1e3]
    ax.plot(data.age*1e3, data, **kwargs)
    ax.text(-time, data[-1], '  '+text.format(float(data[-1])),
            ha='left', va='center', clip_on=True, **kwargs)


def plot_rolling(ax, data, time, text='  {: .0f}', **kwargs):
    """Plot progress line with rolling mean and time tag."""
    roll = data.rolling(age=100, center=True).mean()
    plot_tagline(ax, data, time, text='', alpha=0.5, **kwargs)
    plot_tagline(ax, roll, time, text=text, **kwargs)


def timebar(time, crop='co', mode='co', lang='en', start=-120000, end=0):
    """Plot time bar overlay for given time."""

    # mode-dependent properties
    variables = dict(co=('dt', 'sl'), er=('sl', 'er'), ul=('sl', 'ul'))[mode]
    colors = '0.25', dict(co='C1', er='C11', ul='C3')[mode]

    # initialize figure
    fig, tsax = apl.subplots_mm(figsize=(192, 20), gridspec_kw=dict(
        left=15, right=15, bottom=3, top=6))
    twax = tsax.twinx()

    # import language-dependent labels
    with open('anim_alps_4k_{}_{}_{}.yaml'.format(crop, mode, lang)
              ) as metafile:
        labels = yaml.safe_load(metafile)['Labels']

    # for each axes
    for i, ax in enumerate([tsax, twax]):
        var = variables[i]
        color = colors[i]
        label = labels[i+1]

        # plot corresponding variable
        data = open_variable(variables[i])
        if var == 'er':
            plot_rolling(ax, data, time, text='  {: .1f}', color=color)
        else:
            plot_tagline(ax, data, time, color=color)

        # set axes properties
        format_axes(ax, var, color=color, label=label)
        for key, spine in ax.spines.items():
            spine.set_color(color if key == ['left', 'right'][i] else 'none')

    # add moving cursor and adaptive ticks
    tsax.set_xlim(-start, -end)
    plot_cursor(tsax, time, labels[0], sep=(',' if lang == 'ja' else r'$\,$'))

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'ul', 'zo'])
    parser.add_argument('mode', choices=['co', 'er', 'ul'])
    parser.add_argument('lang', choices=['de', 'en', 'fr', 'it', 'ja', 'nl'])
    args = parser.parse_args()

    # set default font properties
    plt.rc('savefig', dpi=508, facecolor='none')
    plt.rc('axes', facecolor='none')
    if args.lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # start and end of animation
    if args.crop in ('lu', 'ma'):
        start, end, step = -45000, -15000, 10
    else:
        start, end, step = -120000, -0, 40000

    # output frames directory
    outdir = os.path.join(os.environ['HOME'], 'anim',
                          'anim_alps_4k_tbar_{}_{}_{:.0f}{:.0f}'.format(
        args.mode, args.lang, -start/1e3, -end/1e3))

    # iterable arguments to save animation frames
    iter_args = [(timebar, outdir, t, args.crop, args.mode, args.lang, start,
                  end) for t in range(start+step, end+1, step)]

    # create frames directory if missing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
