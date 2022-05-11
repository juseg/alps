#!/usr/bin/env python
# Copyright (c) 2018-2022, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alpine ice sheet 4k animations."""

import re
import os.path
import argparse
import multiprocessing as mp

import yaml
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp

import absplots as apl
import cartowik.conventions as ccv
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr
import hyoga.open
import hyoga.plot


# Color palette
# -------------

# set color cycle to colorbrewer Paired palette
plt.rc('axes', prop_cycle=plt.cycler(color=plt.get_cmap('Paired').colors))


# Figure creation
# ---------------

def subplots_dynamic(region, time, **kwargs):
    """Init figure with and subplot with time-dependent extent."""

    # initial and final plot extent
    extents = dict(
        alpsfix=[(152e3, 1048e3, 4848e3, 5352e3),   # 16:9  896x504 233m@4k
                 (152e3, 1048e3, 4848e3, 5352e3)],  # 16:9  896x504 233m@4k
        lucerne=[(416e3,  512e3, 5200e3, 5254e3),   # 16:9   96x54   25m@4k
                 (392e3,  520e3, 5196e3, 5268e3)],  # 16:9  128x72   33m@4k
        durance=[(234e3,  426e3, 4871e3, 4979e3),   # 16:9  192x108  50m@4k
                 (177e3,  433e3, 4853e3, 4997e3)],  # 16:9  256x144  75m@4k
        zoomout=[(329e3,  521e3, 5096e3, 5204e3),   # 16:9  192x108  50m@4k
                 (152e3, 1048e3, 4848e3, 5352e3)],  # 16:9  896x504 233m@4k
        )[region]

    # init figure with full-frame axes
    fig = apl.figure_mm(figsize=kwargs.pop('figsize', (192, 108)), **kwargs)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.UTM(32))
    ax.spines['geo'].set_visible(False)

    # compute dynamic extent
    start = -45e3 if region in ('lucerne', 'durance') else -120e3
    end = -15e3 if region in ('lucerne', 'durance') else -0e3
    zoom = 1.0*(time-start)/(end-start)  # linear increase between 0 and 1
    zoom = zoom**2*(3-2*zoom)  # smooth zoom factor between 0 and 1
    extent = [c0 + (c1-c0)*zoom for c0, c1 in zip(*extents)]

    # set dynamic extent, return fig and axes
    ax.set_extent(extent, crs=ax.projection)
    return fig, ax


# Map elements
# ------------

def draw_lgm_outline(ax=None, edgecolor='#e31a1c', alpha=0.75):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ccrs.PlateCarree(), lw=0.5,
                      alpha=alpha, edgecolor=edgecolor, facecolor='none')
    del shp


def draw_lgm_faded(time, alpha=0.75, **kwargs):
    """Add LGM outline with fade-in and fade-out effects."""
    tred = (time+25000) / 5000
    fade = tred**4 - 2*tred**2 + 1
    if abs(tred) < 1:
        draw_lgm_outline(alpha=alpha*fade, **kwargs)


def draw_natural_earth(ax=None, style='grey', **kwargs):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '#0978ab' if style == 'wiki' else '0.25'
    facecolor = '#c6ecff' if style == 'wiki' else '0.95'
    kwargs = dict(ax=ax, zorder=0, **kwargs)
    cne.add_rivers(edgecolor=edgecolor, **kwargs)
    cne.add_lakes(edgecolor=edgecolor, facecolor=facecolor, **kwargs)
    cne.add_coastline(edgecolor=edgecolor, linestyles='dashed', **kwargs)


def draw_swisstopo_hydrology(ax=None, style='grey', **kwargs):
    """Add Swisstopo lake and river vectors."""
    swissplus = ccrs.TransverseMercator(
        central_longitude=7.439583333333333,
        central_latitude=46.95240555555556,
        false_easting=2600e3, false_northing=1200e3)

    # get axes if None provided
    ax = ax or plt.gca()
    edgecolor = '#0978ab' if style == 'wiki' else '0.25'
    facecolor = '#c6ecff' if style == 'wiki' else '0.95'

    # draw swisstopo rivers
    filename = '../data/external/25_DKM500_GEWAESSER_LIN.shp'
    shp = cshp.Reader(filename)
    for rec in shp.records():
        symb = rec.attributes['Symbol']
        geom = rec.geometry
        if symb != '':
            ax.add_geometries(
                [geom], swissplus, edgecolor=edgecolor, facecolor='none',
                linewidth=2.5*float(re.sub(r'[^0-9\.]', '', symb)), zorder=0,
                **kwargs)

    # draw swisstopo lakes
    filename = '../data/external/22_DKM500_GEWAESSER_PLY.shp'
    shp = cshp.Reader(filename)
    ax.add_geometries(shp.geometries(), swissplus, edgecolor=edgecolor,
                      facecolor=facecolor, lw=0.25, zorder=0, **kwargs)


def draw_tailored_hydrology(ax=None, **kwargs):
    """Add Natural Earth or Swiss topo vectors depending on axes extent."""

    # get the current window extent
    ax = ax or plt.gca()
    west, east, south, north = ax.get_extent()

    # the reference region containing swisstopo data
    west0, east0, south0, north0 = 265e3, 640e3, 5070e3, 5295e3

    # compute intersection and fraction covered by data
    xoverlap = max(0, min(east, east0)-max(west, west0))
    yoverlap = max(0, min(north, north0)-max(south, south0))
    axesarea = (east-west) * (north-south)
    coverage = xoverlap * yoverlap / axesarea

    # compute layer transparencies
    alpha = (coverage-0.9) / 0.1       # linear increase from 0.9 to 1.0
    alpha = max(0.0, min(1.0, alpha))  # capped between 0 and 1
    alpha = alpha**2*(3-2*alpha)       # smooth transition between 0 and 1

    # plot one or both hydrology layers
    if coverage > 0.9:
        draw_swisstopo_hydrology(ax=ax, alpha=alpha, **kwargs)
    if coverage < 1.0:
        draw_natural_earth(ax=ax, alpha=1-alpha, **kwargs)


# Figure drawing functions
# ------------------------

def figure_colorbar(args):
    """Plot color bar layer."""

    # initialize figure
    fig = apl.figure_mm(figsize=(24, 40))
    cax = fig.add_axes_mm([4, 4, 4, 32])

    # mode dependent properties
    if args.visual == 'erosion':
        levels = [10**i for i in range(-9, 1)]
        kwargs = dict(cmap=plt.get_cmap('YlOrBr'),
                      label='erosion rate ($mm\\,a^{-1}$)',
                      format=mpl.ticker.LogFormatterMathtext(),
                      ticks=levels[::3])  # (cax.locator_params issue #11937)
    elif args.visual == 'bedrock':
        levels = [-100, -50, -20, 0, 2, 5, 10]
        kwargs = dict(cmap=plt.get_cmap('PRGn_r'), label='uplift (m)')

    # add colorbar
    boundaries = [-1e9] + levels + [1e9]
    mpl.colorbar.ColorbarBase(
        ax=cax, alpha=0.75, boundaries=boundaries,
        extend='both', norm=mpl.colors.BoundaryNorm(boundaries, 256), **kwargs)

    # return figure
    return fig


def figure_citymap(time, args):
    """Plot city map layer."""

    # initialize figure
    fig, ax = subplots_dynamic(args.region, time, figsize=(192, 108))

    # draw map elements
    # NOTE it would be possible to make rank depend on plot size
    cne.add_cities(
        ax=ax, lang=args.lang, color='0.25', marker='o', s=6,
        exclude=['Monaco'],
        ranks=range(9 if args.region in ('lucerne', 'durance') else 7))

    # return figure
    return fig


def figure_mainmap(time, args, background=True):
    """Plot main (geographic) layer."""

    # initialize figure
    # NOTE: alternatiely change size, dpi, and thin all the contours
    fig, ax = subplots_dynamic(args.region, time, figsize=(384, 216), dpi=254)

    # estimate sea level drop
    dsl = pd.read_csv(
        '../data/external/spratt2016.txt', comment='#', delimiter='\t',
        encoding='iso8859_15', index_col='age_calkaBP').to_xarray()
    dsl = dsl.SeaLev_shortPC1.dropna('age_calkaBP')
    dsl = min(dsl.interp(age_calkaBP=-time/1e3, method='cubic').values, 0.0)

    # plot interpolated data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with hyoga.open.subdataset(filename, time=time, shift=120000) as ds:

        # compute isostasy and interpolate
        ds = ds.hyoga.assign_isostasy('../data/processed/alpcyc.1km.in.nc')
        interp = ds.hyoga.interp(
            '~/pism/input/boot/alps.srtm.hus12.100m.nc', ax=ax, sigma=5000)
        ds = ds.hyoga.where_thicker()  # needs to come after interp

        # plot specific visual
        kwargs = dict(ax=ax, add_colorbar=False, extend='both')
        if args.visual == 'bedrock':
            interp.hyoga.plot.bedrock_isostasy(
                levels=[-100, -50, -20, 0, 2, 5, 10], **kwargs)
        elif args.visual == 'erosion':
            interp.hyoga.plot.bedrock_erosion(
                levels=[10**i for i in range(-9, 1)], **kwargs)
        elif args.visual == 'velsurf':
            interp.hyoga.plot.surface_velocity(
                vmin=10, vmax=1000, **kwargs)
        elif args.visual == 'streams':
            interp.hyoga.plot.ice_margin(facecolor='w', alpha=0.75)
            ds.hyoga.plot.surface_velocity_streamplot(
                vmin=1e1, vmax=1e3, density=(24, 16))

        # plot common background
        interp.hyoga.plot.bedrock_altitude(
            cmap=ccv.ELEVATIONAL if args.visual == 'streams' else 'Greys',
            vmin=(-4500 if args.visual == 'streams' else 0), vmax=4500,
            ax=ax, sealevel=dsl)
        interp.hyoga.plot.bedrock_shoreline(
            colors=('#0978ab' if args.visual == 'streams' else '0.25'),
            ax=ax, sealevel=dsl)
        csr.add_multishade(interp.topg, ax=ax, add_colorbar=False, zorder=-1)
        interp.hyoga.plot.surface_altitude_contours(major=1000, minor=200)
        interp.hyoga.plot.ice_margin(edgecolor='0.25')

    # draw map elements
    if background is True:
        draw_tailored_hydrology(
            ax=ax, style='wiki' if args.visual == 'streams' else 'grey')
    # FIXME this is not working
    # if args.visual == 'velsurf':
    #     draw_lgm_faded(ax=ax, time=time)

    # return figure
    return fig


# FIXME linearize following methods into figure_tbar
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
    with hyoga.open.dataset(filename) as ds:
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
    if data[-1].notnull():  # as happens with rolling means
        ax.text(-time, data[-1], '  '+text.format(float(data[-1])),
                ha='left', va='center', clip_on=True, **kwargs)


def plot_rolling(ax, data, time, text='  {: .0f}', **kwargs):
    """Plot progress line with rolling mean and time tag."""
    roll = data.rolling(age=100, center=True).mean()
    plot_tagline(ax, data, time, text='', alpha=0.5, **kwargs)
    plot_tagline(ax, roll, time, text=text, **kwargs)


def figure_timebar(time, args, start=-120000, end=0):
    """Plot time bar layer."""

    # mode-dependent properties
    # FIXME streams and velsurf timebars are the same
    variables = dict(
        bedrock=('sl', 'ul'), erosion=('sl', 'er'),
        streams=('dt', 'sl'), velsurf=('dt', 'sl'))[args.visual]
    colors = '0.25', dict(
        bedrock='C3', erosion='C11', streams='C1', velsurf='C1')[args.visual]

    # initialize figure
    fig, tsax = apl.subplots_mm(figsize=(192, 20), gridspec_kw=dict(
        left=15, right=15, bottom=3, top=6))
    twax = tsax.twinx()

    # import language-dependent labels (velsurf use same metadata as streams)
    # FIXME duplicate lines in timetag
    filename = 'alpcyc_4k_{0.visual}_{0.lang}.yaml'.format(args)
    filename = filename.replace('velsurf', 'streams')
    with open(filename) as metafile:
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
    plot_cursor(
        tsax, time, labels[0], sep=(',' if args.lang == 'ja' else r'$\,$'))

    # return figure
    return fig


def figure_timetag(time, args):
    """Plot time tag layer."""

    # initialize figure
    fig = apl.figure_mm(figsize=(32, 6))

    # import language-dependent label (velsurf use same metadata as streams)
    filename = 'alpcyc_4k_{0.visual}_{0.lang}.yaml'.format(args)
    filename = filename.replace('velsurf', 'streams')
    with open(filename) as metafile:
        tag = yaml.safe_load(metafile)['Labels'][0].format(0-time)
    if args.lang != 'ja':
        tag = tag.replace(',', r'$\,$')
    fig.text(2.5/32, 1-2.5/6, tag, ha='left', va='top', fontweight='bold')

    # return figure
    return fig


# Figure saving
# -------------

def save_animation_frame(func, outdir, time, *args, **kwargs):
    """Save figure produced by func as animation frame if missing."""

    # create output directory if missing
    outdir = os.path.expanduser(outdir)
    os.makedirs(outdir, exist_ok=True)

    # check if file exists
    fname = os.path.join(outdir, '{:06d}.png').format(time+120000)
    if not os.path.isfile(fname):

        # assemble figure and save
        print('plotting {:s} ...'.format(fname))
        fig = func(time, *args, **kwargs)
        fig.savefig(fname, dpi='figure')
        plt.close(fig)


# Main program
# ------------

def main():
    """Main program for command-line execution."""

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'region', choices=['alpsfix', 'lucerne', 'durance', 'zoomout'])
    parser.add_argument(
        'visual', choices=['bedrock', 'erosion', 'streams', 'velsurf'])
    parser.add_argument('lang', choices=['de', 'en', 'fr', 'it', 'ja', 'nl'])
    args = parser.parse_args()

    # set matplotlib parametres
    plt.rc('axes', facecolor='none')
    plt.rc('figure', dpi=508, facecolor='none')
    if args.lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # plot colorbar separately
    if args.visual in ('bedrock', 'erosion'):
        fig = figure_colorbar(args)
        fig.savefig(os.path.expanduser(
            '~/anim/alpcyc_4k_{0.visual}_colorbar_{0.lang}.png'.format(args)))
        plt.close(fig)

    # frame output directories
    outdirs = dict(
        citymap='~/anim/alpcyc_4k_{0.region}_citymap_{0.lang}'.format(args),
        mainmap='~/anim/alpcyc_4k_{0.region}_{0.visual}'.format(args),
        timetag='~/anim/alpcyc_4k_timetag_{0.lang}'.format(args),
        timebar='~/anim/alpcyc_4k_timebar_{0.visual}_{0.lang}'.format(args))

    # iterable arguments to save animation frames
    iter_args = []
    if args.region == 'alpsfix':
        iter_args.append((figure_citymap, outdirs['citymap'], 0, args))
        for time in range(-0, -120000, -40):
            iter_args.append((figure_mainmap, outdirs['mainmap'], time, args))
            iter_args.append((figure_timebar, outdirs['timebar'], time, args))
    elif args.region == 'zoomout':
        for time in range(-0, -120000, -40):
            iter_args.append((figure_citymap, outdirs['citymap'], time, args))
            iter_args.append((figure_mainmap, outdirs['mainmap'], time, args))
            iter_args.append((figure_timebar, outdirs['timebar'], time, args))
    else:
        for time in range(-15000, -45000, -10):
            iter_args.append((figure_citymap, outdirs['citymap'], time, args))
            iter_args.append((figure_mainmap, outdirs['mainmap'], time, args))
            iter_args.append((figure_timetag, outdirs['timetag'], time, args))

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
