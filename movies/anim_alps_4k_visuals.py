#!/usr/bin/env python
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps 4k animations frames main visuals."""

import os
import argparse
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pismx.open
import utils as ut

import re
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import cartowik.conventions as ccv
import cartowik.naturalearth as cne
import cartowik.shadedrelief as csr


# Color palette
# -------------

# set color cycle to colorbrewer Paired palette
plt.rc('axes', prop_cycle=plt.cycler(color=plt.get_cmap('Paired').colors))


# Figure creation
# ---------------

def axes_anim_dynamic(crop, t, start=-120e3, end=-0e3, figsize=(192.0, 108.0)):
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
    ax.background_patch.set_fc('none')
    ax.outline_patch.set_ec('none')
    ax.set_rasterization_zorder(2.5)

    # compute dynamic extent
    e0, e1 = ('{}_{:d}'.format(crop, i) for i in (0, 1))
    zoom = 1.0*(t-start)/(end-start)  # linear increase between 0 and 1
    zoom = zoom**2*(3-2*zoom)  # smooth zoom factor between 0 and 1
    extent = [c0 + (c1-c0)*zoom for (c0, c1) in zip(regions[e0], regions[e1])]

    # set dynamic extent, return fig and axes
    ax.set_extent(extent, crs=ax.projection)
    return fig, ax


# Map elements
# ------------

def draw_lgm_outline(ax=None, c='#e31a1c', alpha=0.75):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ccrs.PlateCarree(), lw=0.5,
                      alpha=alpha, edgecolor=c, facecolor='none')
    del shp


def draw_lgm_faded(t, alpha=0.75, **kwargs):
    """Add LGM outline with fade-in and fade-out effects."""
    tred = (t+25000) / 5000
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
        if symb != '':
            lw = 2.5*float(re.sub(r'[^0-9\.]', '', symb))
            ax.add_geometries(geom, swissplus, edgecolor=edgecolor,
                              facecolor='none', lw=lw, zorder=0, **kwargs)

    # draw swisstopo lakes
    filename = '../data/external/22_DKM500_GEWAESSER_PLY.shp'
    shp = cshp.Reader(filename)
    ax.add_geometries(shp.geometries(), swissplus, edgecolor=edgecolor,
                      facecolor=facecolor, lw=lw, zorder=0, **kwargs)


def draw_tailored_hydrology(ax=None, **kwargs):

    # get the current window extent
    ax = ax or plt.gca()
    w, e, s, n = ax.get_extent()

    # the reference region containing swisstopo data
    w0, e0, s0, n0 = 252e3,  636e3, 5072e3, 5288e3  # FIXME ch1 unprecise

    # compute intersection and fraction covered by data
    xoverlap = max(0, min(e, e0)-max(w, w0))
    yoverlap = max(0, min(n, n0)-max(s, s0))
    axesarea = (e-w) * (n-s)
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


# Data input methods
# ------------------

def open_dataset(filename):
    """Open single-file dataset with age coordinate."""
    ds = xr.open_dataset(filename, decode_cf=False)
    if 'time' in ds.coords and 'seconds' in ds.time.units:
        ds = ds.assign_coords(time=ds.time/(365*24*60*60))
    if 'time' in ds.coords:
        ds = ds.assign_coords(age=-ds.time)
    return ds


def open_sealevel(t):
    ds = pd.read_csv('../data/external/spratt2016.txt', comment='#',
                     delimiter='\t', index_col='age_calkaBP').to_xarray()
    ds = ds.SeaLev_shortPC1.dropna('age_calkaBP')
    ds = min(ds.interp(age_calkaBP=-t/1e3, method='cubic').values, 0.0)
    return ds


# Styled plots from data arrays
# -----------------------------

def plot_ice_extent(darray, ax=None, ec='k', fc='none'):
    """Draw void or filled ice extent contour."""

    # plot a single contour
    if ec != 'none':
        darray.plot.contour(ax=ax, colors=[ec], levels=[0.5], linewidths=0.25)
    if fc != 'none':
        darray.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors=fc,
                             extend='neither', levels=[0.5, 1.5])


def plot_topo_contours(darray, ax=None, ec='0.25'):
    """Plot surface topography contours."""

    # contour levels
    levels = range(0, 5000, 200)
    majors = [lev for lev in levels if lev % 1000 == 0]
    minors = [lev for lev in levels if lev % 1000 != 0]

    # plot contours
    darray.plot.contour(ax=ax, colors=[ec], levels=majors, linewidths=0.25)
    darray.plot.contour(ax=ax, colors=[ec], levels=minors, linewidths=0.1)


def plot_shaded_relief(darray, ax=None, mode='gs'):
    """Plot shaded relief map from elevation data array."""

    # plot basal topography
    darray.plot.imshow(
        ax=ax, add_colorbar=False, zorder=-1,
        cmap=(ccv.ELEVATIONAL if mode == 'co' else 'Greys'),
        vmin=(-4500 if mode == 'co' else 0), vmax=4500)
    csr.add_multishade(
        darray, ax=ax, add_colorbar=False, zorder=-1)

    # add coastline if data spans the zero
    if darray.min() * darray.max() < 0.0:
        colors = '#0978ab' if mode == 'co' else '0.25'
        darray.plot.contour(ax=ax, colors=colors, levels=[0.0],
                            linestyles=['dashed'], linewidths=0.25)


def plot_streamlines(dataset, ax=None, **kwargs):
    """Plot surface velocity streamlines."""

    # get current axes if none provided
    ax = ax or plt.gca()

    # extract velocities
    icy = dataset.thk.fillna(0.0) >= 1.0
    uvel = dataset.uvelsurf.where(icy).to_masked_array()
    vvel = dataset.vvelsurf.where(icy).to_masked_array()
    vmag = (uvel**2+vvel**2)**0.5

    # streamplot colormapping fails on empty arrays
    # FIXME report this as a bug in matplotlib
    if uvel.count() * vvel.count() == 0:
        return

    # add streamplot,
    ax.streamplot(dataset.x, dataset.y, uvel, vvel, color=vmag,
                  cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3),
                  arrowsize=0.25, linewidth=0.5, **kwargs)


# Main plotting function
# ----------------------

def visual(time, crop='al', mode='co', start=-120000, end=-0):
    """Plot main figure for given time."""

    # initialize figure
    fig, ax = axes_anim_dynamic(
        crop, time, start=start, end=end, figsize=(384, 216))

    # estimate sea level drop
    dsl = open_sealevel(time)

    # plot interpolated data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with pismx.open.visual(
            filename, '../data/processed/alpcyc.1km.in.nc',
            '../data/external/srtm.nc', ax=ax, time=time, shift=120000) as ds:
        if mode != 'ga':
            plot_shaded_relief(ds.topg-dsl, ax=ax, mode=mode)
            plot_ice_extent(
                ds.icy, ax=ax, fc=('w' if mode in 'co' else 'none'))
        plot_topo_contours(ds.usurf, ax=ax)

    # mode co, stream plot extra data
    if mode == 'co':
        with pismx.open.subdataset(filename, time=time, shift=120000) as ds:
            plot_streamlines(ds, ax=ax, density=(24, 16))

    # mode er, interpolate erosion rate
    # (values range 1e-16 to 1e2, mostly within 1e-12 to 1e-2)
    elif mode == 'er':
        (5.2e-8*ds.velbase_mag**2.34).where(ds.icy).plot.contourf(
            ax=ax, add_colorbar=False, alpha=0.75, cmap='YlOrBr',
            levels=[10**i for i in range(-9, 1)])

    # mode ga or gs, show interpolated velocities
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

    # draw map elements
    if mode != 'ga':
        draw_tailored_hydrology(ax=ax, mode=mode)
    if mode == 'gs':
        draw_lgm_faded(ax=ax, t=time)

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
        start, end, step = -45000, -15000, 10000
    else:
        start, end, step = -120000, -0, 4000

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
