#!/usr/bin/env python
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
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
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp

import absplots as apl
import cartowik.conventions as ccv
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr
import pismx.open


# Color palette
# -------------

# set color cycle to colorbrewer Paired palette
plt.rc('axes', prop_cycle=plt.cycler(color=plt.get_cmap('Paired').colors))


# Figure creation
# ---------------

def axes_anim_dynamic(crop, time, start=-120e3, end=-0e3, **kwargs):
    """Init dynamic extent figure and subplot."""

    # predefined crop regions
    regions = dict(
        al_0=(120e3, 1080e3, 4835e3, 5375e3),  # Alps   16:9  960x540 250m@4k
        al_1=(120e3, 1080e3, 4835e3, 5375e3),  # "
        ch_0=(380e3,  476e3, 5120e3, 5174e3),  # Switz. 16:9   96x54   25m@4k
        ch_1=(252e3,  636e3, 5072e3, 5288e3),  # Switz. 16:9  384x216 100m@4k
        lu_0=(416e3,  512e3, 5200e3, 5254e3),  # Luzern 16:9   96x54   25m@4k
        lu_1=(392e3,  520e3, 5196e3, 5268e3),  # Luzern 16:9  128x72   33m@4k
        ma_0=(234e3,  426e3, 4871e3, 4979e3),  # Marit. 16:9  192x108  50m@4k
        ma_1=(141e3,  429e3, 4829e3, 4991e3),  # Marit. 16:9  288x162  75m@4k
        ul_0=(152e3, 1048e3, 4848e3, 5352e3),  # Uplift 16:9  896x504 233m@4k
        ul_1=(152e3, 1048e3, 4848e3, 5352e3),  # "
        zo_0=(329e3,  521e3, 5096e3, 5204e3),  # Switz. 16:9  192x108  50m@4k
        zo_1=(120e3, 1080e3, 4835e3, 5375e3),  # Alps   16:9  960x540 250m@4k
    )

    # init figure with full-frame axes
    fig = apl.figure_mm(figsize=kwargs.pop('figsize', (192, 108)), **kwargs)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.UTM(32))
    fig.set_dpi(254)  # NOTE: or change size, and thin all the contours
    ax.spines['geo'].set_visible(False)

    # compute dynamic extent
    extents = (regions['{}_{:d}'.format(crop, i)] for i in (0, 1))
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


def draw_major_cities(ax=None, exclude=None, include=None, maxrank=5,
                      textoffset=2, lang='en'):
    """Add major city locations with names."""
    ax = ax or plt.gca()

    # get axes extent
    west, east, south, north = ax.get_extent()

    # relative label positions
    xloc = 'r'  # ('l' if xc < center[0] else 'r')
    yloc = 'u'  # ('l' if yc < center[1] else 'u')
    dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
    dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
    ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
    va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]

    # open shapefile data
    shp = cshp.Reader(cshp.natural_earth(
        resolution='10m', category='cultural', name='populated_places'))

    # loop on records
    for rec in shp.records():
        name = rec.attributes['name_'+lang]
        rank = rec.attributes['SCALERANK']

        # check rank and name
        if rank > maxrank and name not in include or name in exclude:
            continue

        # check location
        geom = rec.geometry
        crs = ccrs.PlateCarree()
        x, y = ax.projection.transform_point(geom.x, geom.y, src_crs=crs)
        if west > x or x > east or south > y or y > north:
            continue

        # plot
        ax.plot(x, y, marker='o', color='0.25', ms=2)
        ax.annotate(name, xy=(x, y), xytext=(dx, dy), color='0.25',
                    textcoords='offset points', ha=ha, va=va, clip_on=True)


def draw_natural_earth(ax=None, mode='gs', **kwargs):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '#0978ab' if mode == 'co' else '0.25'
    facecolor = '#c6ecff' if mode == 'co' else '0.95'
    kwargs = dict(ax=ax, zorder=0, **kwargs)
    cne.add_rivers(edgecolor=edgecolor, **kwargs)
    cne.add_lakes(edgecolor=edgecolor, facecolor=facecolor, **kwargs)
    cne.add_coastline(edgecolor=edgecolor, **kwargs)


def draw_swisstopo_hydrology(ax=None, mode='gs', **kwargs):
    """Add Swisstopo lake and river vectors."""
    swissplus = ccrs.TransverseMercator(
        central_longitude=7.439583333333333,
        central_latitude=46.95240555555556,
        false_easting=2600e3, false_northing=1200e3)

    # get axes if None provided
    ax = ax or plt.gca()
    edgecolor = '#0978ab' if mode == 'co' else '0.25'
    facecolor = '#c6ecff' if mode == 'co' else '0.95'

    # draw swisstopo rivers
    filename = '../data/external/25_DKM500_GEWAESSER_LIN.shp'
    shp = cshp.Reader(filename)
    for rec in shp.records():
        symb = rec.attributes['Symbol']
        geom = rec.geometry
        help(geom)
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

def figure_cbar(mode='er'):
    """Plot color bar layer."""

    # initialize figure
    fig = apl.figure_mm(figsize=(24, 40))
    cax = fig.add_axes_mm([4, 4, 4, 32])

    # mode dependent properties
    if mode == 'er':
        levels = [10**i for i in range(-9, 1)]
        kwargs = dict(cmap=plt.get_cmap('YlOrBr'),
                      label='erosion rate ($mm\\,a^{-1}$)',
                      format=mpl.ticker.LogFormatterMathtext(),
                      ticks=levels[::3])  # (cax.locator_params issue #11937)
    elif mode == 'ul':
        levels = [-100, -50, -20, 0, 2, 5, 10]
        kwargs = dict(cmap=plt.get_cmap('PRGn_r'), label='uplift (m)')

    # add colorbar
    boundaries = [-1e9] + levels + [1e9]
    mpl.colorbar.ColorbarBase(
        ax=cax, alpha=0.75, boundaries=boundaries,
        extend='both', norm=mpl.colors.BoundaryNorm(boundaries, 256), **kwargs)

    # return figure
    return fig


def figure_city(time, crop='al', lang='en', start=-120e3, end=0e3):
    """Plot city map layer."""

    # initialize figure
    fig, ax = axes_anim_dynamic(
        crop, time, start=start, end=end, figsize=(192, 108))

    # draw map elements
    # FIXME move cities to cartowik?
    draw_major_cities(ax=ax, exclude='Monaco', include='Sion', lang=lang,
                      maxrank=(8 if crop in ('lu', 'ma') else 6))

    # return figure
    return fig


def figure_main(time, crop='al', mode='co', start=-120000, end=-0):
    """Plot main (geographic) layer."""

    # initialize figure
    # NOTE: alternatiely change size, dpi, and thin all the contours
    fig, ax = axes_anim_dynamic(
        crop, time, start=start, end=end, figsize=(384, 216), dpi=254)

    # estimate sea level drop
    dsl = pd.read_csv('../data/external/spratt2016.txt', comment='#',
                      delimiter='\t', index_col='age_calkaBP').to_xarray()
    dsl = dsl.SeaLev_shortPC1.dropna('age_calkaBP')
    dsl = min(dsl.interp(age_calkaBP=-time/1e3, method='cubic').values, 0.0)

    # plot interpolated data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with pismx.open.visual(
            filename, bootfile='../data/processed/alpcyc.1km.in.nc',
            interpfile='../data/external/srtm.nc', ax=ax, time=time,
            shift=120000, sigma=10000) as ds:

        # shaded relief topographic background
        if mode != 'ga':
            (ds.topg-dsl).plot.imshow(
                ax=ax, add_colorbar=False, zorder=-1,
                cmap=(ccv.ELEVATIONAL if mode == 'co' else 'Greys'),
                vmin=(-4500 if mode == 'co' else 0), vmax=4500)
            csr.add_multishade(
                ds.topg, ax=ax, add_colorbar=False, zorder=-1)
            ds.topg.plot.contour(
                ax=ax, colors=('#0978ab' if mode == 'co' else '0.25'),
                levels=[dsl], linestyles='dashed', linewidths=0.25, zorder=0)
            ds.thk.notnull().plot.contour(
                ax=ax, colors=['k'], levels=[0.5], linewidths=0.25)

        # always plot topo contours
        ds.usurf.plot.contour(
            levels=[lev for lev in range(0, 5000, 200) if lev % 1000 == 0],
            ax=ax, colors=['0.25'], linewidths=0.25)
        ds.usurf.plot.contour(
            levels=[lev for lev in range(0, 5000, 200) if lev % 1000 != 0],
            ax=ax, colors=['0.25'], linewidths=0.1)

        # streamline plot outer contour
        if mode == 'co':
            ds.thk.notnull().plot.contourf(
                ax=ax, add_colorbar=False, alpha=0.75, colors='w',
                extend='neither', levels=[0.5, 1.5])

        # erosion rate (values 1e-16 to 1e2, mostly 1e-12 to 1e-2)
        elif mode == 'er':
            (5.2e-8*ds.velbase_mag**2.34).plot.contourf(
                ax=ax, add_colorbar=False, alpha=0.75, cmap='YlOrBr',
                levels=[10**i for i in range(-9, 1)])

        # velocities map
        elif mode in ('ga', 'gs'):
            ds.velsurf_mag.plot.imshow(
                ax=ax, add_colorbar=False, alpha=0.75,
                cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3))

        # mode ul, show interpolated bedrock depression
        elif mode == 'ul':
            ds.uplift.plot.contourf(
                ax=ax, add_colorbar=False, alpha=0.75, cmap='PRGn_r',
                levels=[-100, -50, -20, 0, 2, 5, 10])

            # locate maximum depression (xarray has no idxmin yet)
            i, j = divmod(int(ds.uplift.argmin()), ds.uplift.shape[1])
            maxdep = float(-ds.uplift[i, j])
            color = 'w' if maxdep > 50 else 'k'
            ax.plot(ds.x[j], ds.y[i], 'o', color=color, alpha=0.75)
            ax.text(ds.x[j]+5e3, ds.y[i]+5e3, '{:.0f} m'.format(maxdep),
                    color=color)

    # mode co, stream plot extra data
    if mode == 'co':
        with pismx.open.subdataset(filename, time=time, shift=120000) as ds:

            # streamplot colormapping fails on empty arrays (mpl issue #19323)
            ds['icy'] = ds.thk.fillna(0.0) >= 1.0
            if ds.icy.count() > 0:
                ax.streamplot(
                    ds.x, ds.y,
                    ds.uvelsurf.where(ds.icy).to_masked_array(),
                    ds.vvelsurf.where(ds.icy).to_masked_array(),
                    color=((ds.uvelsurf**2+ds.vvelsurf**2)**0.5
                           ).to_masked_array(),
                    cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3),
                    arrowsize=0.25, linewidth=0.5, density=(24, 16))

    # draw map elements
    if mode != 'ga':
        draw_tailored_hydrology(ax=ax, mode=mode)
    if mode == 'gs':
        draw_lgm_faded(ax=ax, time=time)

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


def figure_tbar(time, crop='co', mode='co', lang='en', start=-120000, end=0):
    """Plot time bar layer."""

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


def figure_ttag(t, lang='en'):
    """Plot time tag layer."""

    # initialize figure
    figw, figh = 32.0, 6.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))

    # import language-dependent label
    with open('anim_alps_4k_zo_co_{}.yaml'.format(lang)) as f:
        tag = yaml.safe_load(f)['Labels'][0].format(0-t)
    if lang != 'ja':
        tag = tag.replace(',', r'$\,$')
    fig.text(2.5/figw, 1-2.5/figh, tag, ha='left', va='top', fontweight='bold')

    # return figure
    return fig


# Figure saving
# -------------

def save_animation_frame(func, outdir, t, *args, **kwargs):
    """Save figure produced by func as animation frame if missing."""

    # create output directory if missing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # check if file exists
    fname = os.path.join(outdir, '{:06d}.png').format(t+120000)
    if not os.path.isfile(fname):

        # assemble figure and save
        print('plotting {:s} ...'.format(fname))
        fig = func(t, *args, **kwargs)
        fig.savefig(fname, transparent=True, dpi='figure')
        plt.close(fig)


# Main program
# ------------

def main():
    """Main program for command-line execution."""

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'ul', 'zo'])
    parser.add_argument('mode', choices=['co', 'er', 'ga', 'gs', 'ul'])
    parser.add_argument('lang', choices=['de', 'en', 'fr', 'it', 'ja', 'nl'])
    args = parser.parse_args()

    # set matplotlib parametres
    plt.rc('axes', facecolor='none')
    plt.rc('figure', dpi=508, facecolor='none')
    if args.lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # start and end of animation
    if args.crop in ('lu', 'ma'):
        start, end, step = -45000, -15000, 10
    else:
        start, end, step = -120000, -0, 4000

    # plot colorbar separately
    prefix = '/run/media/julien/coldroom/anim/anim_alps_4k'
    fig = figure_cbar(args.mode)
    fig.savefig('{}_cbar_{}_{}.png'.format(prefix, args.mode, args.lang))
    plt.close(fig)

    # iterable arguments to save animation frames
    time_range = range(start+step, end+1, step)
    city_range = [end] if args.crop in ('al', 'ul') else time_range
    iter_args = []
    for time in city_range:
        iter_args.append(
            (figure_city, '{}_city_{}_{}'.format(prefix, args.crop, args.lang),
             time, args.crop, args.lang, start, end))
    for time in time_range:
        iter_args.append(
            (figure_main, '{}_main_{}_{}'.format(prefix, args.crop, args.mode),
             time, args.crop, args.mode, start, end))
        iter_args.append(
            (figure_tbar, '{}_tbar_{}_{}_{:.0f}{:.0f}'.format(
                prefix, args.mode, args.lang, -start/1e3, -end/1e3),
             time, args.crop, args.mode, args.lang, start, end))
        iter_args.append(
            (figure_ttag, '{}_ttag_{}_{:.0f}{:.0f}'.format(
                prefix, args.lang, -start/1e3, -end/1e3),
             time, args.lang))

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
