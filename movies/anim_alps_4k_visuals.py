#!/usr/bin/env python
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps 4k animations frames main visuals."""

import os
import re
import argparse
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import cartowik.conventions as ccv
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr
import pismx.open
import utils as ut


# Color palette
# -------------

# set color cycle to colorbrewer Paired palette
plt.rc('axes', prop_cycle=plt.cycler(color=plt.get_cmap('Paired').colors))


# Figure creation
# ---------------

def axes_anim_dynamic(crop, time, start=-120e3, end=-0e3, figsize=(192, 108)):
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
    figw, figh = figsize
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.UTM(32))
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


# Main plotting function
# ----------------------

def visual(time, crop='al', mode='co', start=-120000, end=-0):
    """Plot main figure for given time."""

    # initialize figure
    fig, ax = axes_anim_dynamic(
        crop, time, start=start, end=end, figsize=(384, 216))

    # estimate sea level drop
    dsl = pd.read_csv('../data/external/spratt2016.txt', comment='#',
                      delimiter='\t', index_col='age_calkaBP').to_xarray()
    dsl = dsl.SeaLev_shortPC1.dropna('age_calkaBP')
    dsl = min(dsl.interp(age_calkaBP=-time/1e3, method='cubic').values, 0.0)

    # plot interpolated data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with pismx.open.visual(
            filename, '../data/processed/alpcyc.1km.in.nc',
            '../data/external/srtm.nc', ax=ax, time=time, shift=120000) as ds:

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
                ax=ax, colors=['0.25'], levels=[0.5], linewidths=0.25)

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


def main():
    """Main program for command-line execution."""

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'ul', 'zo'])
    parser.add_argument('mode', choices=['co', 'er', 'ga', 'gs', 'ul'])
    args = parser.parse_args()

    # set default font size for uplift tag and colorbars
    plt.rc('font', size=12)

    # start and end of animation
    if args.crop in ('lu', 'ma'):
        start, end, step = -45000, -15000, 10
    else:
        start, end, step = -120000, -0, 40

    # output frame directories
    prefix = os.path.join(os.environ['HOME'], 'anim', 'anim_alps_4k')
    outdir = prefix + '_main_' + args.crop + '_' + args.mode

    # iterable arguments to save animation frames
    iter_args = [(visual, outdir, t, args.crop, args.mode, start, end)
                 for t in range(start+step, end+1, step)]

    # create frame directory if missing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=8) as pool:
        pool.starmap(ut.save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
