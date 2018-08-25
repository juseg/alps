#!/usr/bin/env python2
# coding: utf-8

"""Plotting functions."""

import os
import re
import sys
import util as ut
import numpy as np
import scipy.interpolate as sinterp
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp
import iceplotlib.plot as iplt
import iceplotlib.cm as icm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.collections as mcollections
import matplotlib.transforms as mtransforms

# Color palette
# -------------

# color brewer Paired palette
colorkeys = [tone+hue
             for hue in ('blue', 'green', 'red', 'orange', 'purple', 'brown')
             for tone in ('light', 'dark')]
colorvals = iplt.get_cmap('Paired', 12)(range(12))
palette = dict(zip(colorkeys, colorvals))

# personal colormaps
# FIXME move to iceplotlib
cols = [(0.0, (0,0,0,0)), (1.0, (0,0,0,1))]  # transparent to black
shademap = mcolors.LinearSegmentedColormap.from_list('shades', cols)
cols = [(0.0, (1,1,1,0)), (1.0, (1,1,1,1))]  # transparent to white
whitemap = mcolors.LinearSegmentedColormap.from_list('whites', cols)
cols = [(0.0, (1,1,1,1)), (0.5, (1,1,1,0)),
        (0.5, (0,0,0,0)), (1.0, (0,0,0,1))]  # white transparent black
shinemap = mcolors.LinearSegmentedColormap.from_list('shines', cols)


# Mapping properties
# ------------------

# velocity norm
velnorm = mcolors.LogNorm(1e1, 1e3)

# contour levels
topolevs = range(0, 5000, 200)
inlevs = [l for l in topolevs if l % 1000 != 0]
utlevs = [l for l in topolevs if l % 1000 == 0]


# Geographic data
# ---------------

# geographic projections
ll = ccrs.PlateCarree()
utm = ccrs.UTM(32)
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)
swissplus = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=2600e3, false_northing=1200e3)
stereo = ccrs.Stereographic(central_latitude=0.0, central_longitude=7.5)

# geographic regions
regions = {'egu': (112.5e3, 1087.5e3, 4855e3, 5355e3), # egu poster 975x500
           '1609': (120e3, 1080e3, 4835e3, 5375e3),    # alps 16:9 960x540
           'alps': (150e3, 1050e3, 4820e3, 5420e3),    # model domain 900x600
           'bern': (390e3, 465e3, 5125e3, 5175e3),     # Bern 75x50
           'crop': (155e3, 1045e3, 4825e3, 5415e3),    # 5 km crop 890x590
           'guil': (230e3, 470e3, 5050e3, 5240e3),     # Guillaume 240x190
           'west': (250e3, 700e3, 4970e3, 5270e3),     # western 450x300
           'inn':   (500e3, 815e3, 5125e3, 5350e3),    # Inn 315x225
           'isere': (230e3, 370e3, 5000e3, 5100e3),    # Isère 140x100
           'ivrea': (300e3, 440e3, 5000e3, 5100e3),    # Ivrea 140x100
           'rhine': (410e3, 620e3, 5150e3, 5300e3),    # Rhine 210x150
           'rhone': (300e3, 475e3, 5100e3, 5225e3),    # Rhone 175x125
           'reuss0': (416e3, 512e3, 5200e3, 5254e3),   # Luzern  96x54 km
           'reuss1': (392e3, 520e3, 5196e3, 5268e3),   # Luzern 128x72 km
           'swiss0': (380e3, 476e3, 5120e3, 5174e3),   # Swiss  96x54 km
           'swiss1': (252e3, 636e3, 5072e3, 5288e3),   # Swiss 384x216 km
           'rhlobe': (450e3, 600e3, 5225e3, 5325e3),   # Rhine lobe 150x100
           'taglia': (760e3, 865e3, 5105e3, 5180e3),   # Tagliamento 105x75
           'valais': (310e3, 460e3, 5065e3, 5165e3),   # Trimlines 150x100
           'aletsch': (414e3, 444e3, 5139e3, 5159e3)}  # Aletsch 30x20

# cartopy features monochromatic
ne_rivers = cfeature.NaturalEarthFeature(
    category='physical', name='rivers_lake_centerlines', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.5)
ne_lakes = cfeature.NaturalEarthFeature(
    category='physical', name='lakes', scale='10m',
    edgecolor='0.25', facecolor='0.85', lw=0.25)
ne_coastline = cfeature.NaturalEarthFeature(
    category='physical', name='coastline', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.25)
ne_countries = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_0_boundary_lines_land', scale='10m',
    edgecolor='0.75', facecolor='none', lw=0.50, linestyle='-.')
ne_graticules = cfeature.NaturalEarthFeature(
    category='physical', name='graticules_1', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.1)

# cartopy features color
# FIXME actually it is possible to change the color at plotting time
# FIXME add rivers_europe and lakes_europe
ne_rivers_color = cfeature.NaturalEarthFeature(
    category='physical', name='rivers_lake_centerlines', scale='10m',
    edgecolor='#0978ab', facecolor='none', lw=0.5)
ne_lakes_color = cfeature.NaturalEarthFeature(
    category='physical', name='lakes', scale='10m',
    edgecolor='#0978ab', facecolor='#c6ecff', lw=0.25)
ne_coastline_color = cfeature.NaturalEarthFeature(
    category='physical', name='coastline', scale='10m',
    edgecolor='#0978ab', facecolor='none', lw=0.25)
ne_countries_color = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_0_boundary_lines_land', scale='10m',
    edgecolor='#646464', facecolor='none', lw=0.5, linestyle='-.')
ne_graticules_color = cfeature.NaturalEarthFeature(
    category='physical', name='graticules_1', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.1)


# Convert between coords and extent
# ---------------------------------


def extent_from_coords(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n


def coords_from_extent(extent, cols, rows):
    """Compute coordinate vectors from image extent."""

    # compute dx and dy
    (w, e, s, n) = extent
    dx = (e-w) / cols
    dy = (n-s) / rows

    # prepare coordinate vectors
    xwcol = w + 0.5*dx  # x-coord of W row cell centers
    ysrow = s + 0.5*dy  # y-coord of N row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow + np.arange(rows)*dy  # from S to N

    # return coordinate vectors
    return x, y



# Geographic analysis
# -------------------

def shading(z, dx=None, dy=None, extent=None, azimuth=315.0, altitude=30.0,
            transparent=False):
    """Compute shaded relief map."""
    # FIXME: move to iceplotlib / cartowik and fix potential bugs there

    # get horizontal resolution
    if (dx is None or dy is None) and (extent is None):
        raise ValueError("Either dx and dy or extent must be given.")
    rows, cols = z.shape
    dx = dx or (extent[1]-extent[0])/cols
    dy = dy or (extent[3]-extent[2])/rows

    # convert to rad
    azimuth = azimuth*np.pi / 180.
    altitude = altitude*np.pi / 180.

    # compute cartesian coords of the illumination direction
    # for transparent shades set horizontal surfaces to zero
    xlight = np.sin(azimuth) * np.cos(altitude)
    ylight = np.cos(azimuth) * np.cos(altitude)
    zlight = (0.0 if transparent else np.sin(altitude))

    # compute hillshade (minus dot product of normal and light direction)
    v, u = np.gradient(z, dy, dx)
    shade = - (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)
    return shade


# Axes preparation
# ----------------

def cut_ts_axes(ax, tsw=2/3., tsh=1/3.):
    """Cut timeseries inset into main axes."""
    fig = ax.figure
    pos = ax.get_position()
    figw, figh = fig.get_size_inches()*25.4
    ax.outline_patch.set_ec('none')
    x = [0.0, 1-tsw, 1-tsw, 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, tsh, tsh, 1.0, 1.0, 0.0]
    commkw = dict(clip_on=False, transform=ax.transAxes, zorder=3)
    polykw = dict(ec='k', fc='none', **commkw)
    rectkw = dict(ec='w', fc='w', **commkw)
    poly = iplt.Polygon(zip(x, y), **polykw)
    rect = iplt.Rectangle((1-tsw, 0.0), tsw, tsh, **rectkw)
    tsax = fig.add_axes([pos.x1-tsw*(pos.x1-pos.x0)+12.0/figw, 9.0/figh,
                         tsw*(pos.x1-pos.x0)-24.0/figw,
                         tsh*(pos.y1-pos.y0)-15.0/figh])
    ax.add_patch(rect)
    ax.add_patch(poly)
    return tsax


def cut_ts_sc_axes(ax, tsw=2/3., tsh=1/3., scw=1/5., sch=1/3.):
    """Cut timeseries and scatter plot insets into main axes."""
    fig = ax.figure
    pos = ax.get_position()
    figw, figh = fig.get_size_inches()*25.4
    ax.outline_patch.set_ec('none')
    x = [0.0, 1-tsw, 1-tsw, 1.0, 1.0, scw, scw, 0.0, 0.0]
    y = [0.0, 0.0, tsh, tsh, 1.0, 1.0, 1-sch, 1-sch, 0.0]
    commkw = dict(clip_on=False, transform=ax.transAxes, zorder=3)
    polykw = dict(ec='k', fc='none', **commkw)
    rectkw = dict(ec='w', fc='w', **commkw)
    poly = iplt.Polygon(zip(x, y), **polykw)
    screct = iplt.Rectangle((0.0, 1-sch), scw, sch, **rectkw)
    tsrect = iplt.Rectangle((1-tsw, 0.0), tsw, tsh, **rectkw)
    scax = fig.add_axes([pos.x0+7.5/figw, pos.y1-sch*(pos.y1-pos.y0)+9.0/figh,
                         scw*(pos.x1-pos.x0)-9.0/figw,
                         sch*(pos.y1-pos.y0)-9.0/figh])
    tsax = fig.add_axes([pos.x1-tsw*(pos.x1-pos.x0)+12.0/figw, 9.0/figh,
                         tsw*(pos.x1-pos.x0)-24.0/figw,
                         tsh*(pos.y1-pos.y0)-15.0/figh])
    scax.add_patch(screct)
    tsax.add_patch(poly)
    tsax.add_patch(tsrect)
    return tsax, scax


def cut_sc_hs_pf_axes(ax, tsw=2/3., tsh=1/3.):
    """Cut scatter plots and profiles axes."""
    fig = ax.figure
    pos = ax.get_position()
    figw, figh = fig.get_size_inches()*25.4
    ax.outline_patch.set_ec('none')
    x = [0.0, 1-tsw, 1-tsw, 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, tsh, tsh, 1.0, 1.0, 0.0]
    commkw = dict(clip_on=False, transform=ax.transAxes)
    polykw = dict(ec='k', fc='none', zorder=3, **commkw)
    rectkw = dict(ec='w', fc='w', zorder=3, **commkw)
    poly = iplt.Polygon(zip(x, y), **polykw)
    tsrect = iplt.Rectangle((1-tsw, 0.0), tsw, tsh, **rectkw)
    scah = pos.y0*figh-10.5
    hsaw = (pos.x1-tsw*(pos.x1-pos.x0))*figw-scah-21.0
    scax = fig.add_axes([12.0/figw, 9.0/figh, scah/figw, scah/figh])
    hsax = fig.add_axes([(13.5+scah)/figw, 9.0/figh, 9.0/figw, scah/figh])
    spec = dict(left=(pos.x1-tsw*(pos.x1-pos.x0))*figw+1.5, right=12.0,
                bottom=9.0, top=(pos.y0+tsh*(pos.y1-pos.y0))*figh+1.5,
                hspace=1.5, wspace=1.5)
    grid = fig.subplots_mm(nrows=4, ncols=1, sharex=True, sharey=False,
                           gridspec_kw=spec)
    ax.add_patch(tsrect)
    ax.add_patch(poly)
    return scax, hsax, grid


def prepare_map_axes(ax, extent='alps'):
    """Prepare map axes before plotting."""
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(regions[extent], crs=ax.projection)


def prepare_ts_axes(ax, dt=True, mis=True, t=0.0):
    """Prepare timeseries axes before plotting."""
    if dt is True:
        plot_dt(ax, t=t)
    if mis is True:
        plot_mis(ax)


def set_dynamic_extent(ax=None, t=0, e0='alps', e1='alps', t0=-120e3, t1=-0e3):
    ax = ax or iplt.gca()
    zf = 1.0*(t-t0)/(t1-t0)  # linear increase between 0 and 1
    zf = zf**2*(3-2*zf)  # smooth zoom factor between 0 and 1
    axe = [c0 + (c1-c0)*zf for (c0, c1) in zip(regions[e0], regions[e1])]
    ax.set_extent(axe, crs=ax.projection)


# Single map subplot helpers
# --------------------------

def subplots_ts(nrows=1, ncols=1, sharex=True, sharey=False,
                mode='column', labels=True):
    """Init figure with margins adapted for simple timeseries."""
    figw, figh = (177.0, 85.0) if mode == 'page' else (85.0, 60.0)
    fig, grid = iplt.subplots_mm(nrows=nrows, ncols=ncols,
                                 sharex=sharex, sharey=sharey,
                                 figsize=(figw, figh),
                                 gridspec_kw=dict(left=12.0, right=1.5,
                                                  bottom=9.0, top=1.5,
                                                  hspace=1.5, wspace=1.5))
    if nrows*ncols > 1 and labels is True:
        for ax, l in zip(grid, list('abcdef')):
            add_subfig_label('({})'.format(l), ax=ax)
    return fig, grid


def subplots_anim(extent='1609', figsize=(192.0, 108.0)):
    """Init figure with unique subplot for animation."""
    # FIXME make 4k 16:9 the default for all animations?
    fig, ax = iplt.subplots_mm(figsize=figsize, projection=utm,
                               gridspec_kw=dict(left=0.0, right=0.0,
                                                bottom=0.0, top=0.0))
    ax.outline_patch.set_ec('none')
    ax.background_patch.set_fc('none')
    prepare_map_axes(ax, extent=extent)
    return fig, ax


def subplots_cax(extent='alps'):
    """Init figure with unique subplot and colorbar inset."""
    figw, figh = 177.0, 119.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=1.5, right=1.5,
                                                bottom=1.5, top=1.5))
    cax = fig.add_axes([4.5/figw, 1-52.0/figh, 3.0/figw, 40.0/figh])
    prepare_map_axes(ax, extent=extent)
    return fig, ax, cax


def subplots_cax_anim_1609(extent='alps', labels=False, dt=True, mis=True, t=0.0):
    """Init figure with unique subplot for 16:9 animation."""
    figw, figh = 192.0, 108.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=0.0, right=0.0,
                                                bottom=0.0, top=0.0))
    cax = fig.add_axes([5.0/figw, 1-50.0/figh, 5.0/figw, 40.0/figh])
    ax.outline_patch.set_ec('none')
    prepare_map_axes(ax, extent=extent)
    return fig, ax, cax


def subplots_cax_ts(extent='alps', labels=True, dt=True, mis=True):
    """Init figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 177.0, 119.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=1.5, right=1.5,
                                                bottom=1.5, top=1.5))
    cax = fig.add_axes([4.5/figw, 1-50.5/figh, 3.0/figw, 40.0/figh])
    tsax = cut_ts_axes(ax)
    prepare_map_axes(ax, extent=extent)
    prepare_ts_axes(tsax, dt=dt, mis=mis)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax, tsax


def subplots_cax_ts_sc(extent='alps', labels=True, dt=True, mis=True):
    """Init with subplot, colorbar, timeseries and scatter plot."""
    figw, figh = 177.0, 119.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=1.5, right=1.5,
                                                bottom=1.5, top=1.5))
    cax = fig.add_axes([0.5-20.0/figw, 1-6.0/figh, 40.0/figw, 3.0/figh])
    tsax, scax = cut_ts_sc_axes(ax) #, scw=35.0/174.0, sch=37.5/116.0)
    prepare_map_axes(ax, extent=extent)
    prepare_ts_axes(tsax, dt=dt, mis=mis)
    if labels is True:
        add_subfig_label('(a)', ax=ax, x=0.2)
        add_subfig_label('(b)', ax=scax)
        add_subfig_label('(c)', ax=tsax)
    return fig, ax, cax, tsax, scax


def subplots_cax_sc_hs_pf(extent='alps', labels=True, dt=True, mis=True):
    """Init with subplot, colorbar, scatter plot, histogram and profiles."""
    figw, figh = 177.0, 119.0+39.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=1.5, right=1.5,
                                                bottom=39.0+1.5, top=1.5))
    cax = fig.add_axes([4.5/figw, 1-50.5/figh, 3.0/figw, 40.0/figh])
    scax, hsax, grid = cut_sc_hs_pf_axes(ax)
    prepare_map_axes(ax, extent=extent)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=scax)
        add_subfig_label('(c)', ax=hsax)
        # FIXME region labels
        for i, tsax in enumerate(grid):
            plot_mis(tsax, y=(0.15 if i == 4-1 else None))
            add_subfig_label('(%s)' % 'defg'[i], ax=tsax)
    return fig, ax, cax, scax, hsax, grid


def subplots_cax_ts_anim(extent='alps', labels=False, dt=True, mis=True,
                         t=0.0):
    """Init figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 180.0, 120.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=0.0, right=0.0,
                                                bottom=0.0, top=0.0))
    cax = fig.add_axes([5.0/figw, 70.0/figh, 5.0/figw, 40.0/figh])
    tsax = fig.add_axes([75.0/figw, 10.0/figh, 90.0/figw, 22.5/figh])
    ax.outline_patch.set_ec('none')
    x = [1/3., 1/3., 1.0]
    y = [0.0, 1/3., 1/3.]
    line = iplt.Line2D(x, y, color='k', clip_on=False,
                       transform=ax.transAxes, zorder=3)
    rect = iplt.Rectangle((1/3., 0.0), 2/3., 1/3., ec='w', fc='w',
                          clip_on=False, transform=ax.transAxes, zorder=-1)
    tsax.add_line(line)
    tsax.add_patch(rect)
    prepare_map_axes(ax, extent=extent)
    prepare_ts_axes(tsax, dt=dt, mis=mis, t=t)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax, tsax


def subplots_cax_ts_egu(extent='egu', labels=False, dt=True, mis=True):
    """Init large figure with subplot, colorbar and timeseries insets."""
    figw, figh = 975.0, 500.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=0.0, right=0.0,
                                                bottom=0.0, top=0.0))
    cax1 = fig.add_axes([20.0/figw, 60.0/figh, 50.0/figw, 5.0/figh])
    cax2 = fig.add_axes([20.0/figw, 40.0/figh, 50.0/figw, 5.0/figh])
    ax.outline_patch.set_ec('none')
    prepare_map_axes(ax, extent=extent)
    tsax = None
    return fig, ax, cax1, cax2, tsax


def subplots_cax_ts_sgm(extent='alps', labels=False, dt=True, mis=True):
    """Init A3 figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 405.0, 271 + 1/3.
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=2.5, right=2.5,
                                                bottom=2.5, top=2.5))
    cax1 = fig.add_axes([12.5/figw, 1-32.5/figh, 50.0/figw, 5.0/figh])
    cax2 = fig.add_axes([12.5/figw, 1-52.5/figh, 50.0/figw, 5.0/figh])
    tsax = fig.add_axes([147.5/figw, 15.0/figh, 240.0/figw, 60.0/figh])
    ax.outline_patch.set_ec('none')
    xcut = 130.0/400.0  # ca. 1/3.
    ycut = 85.0/400.0*3/2  # ca. 1/3.
    x = [0.0, xcut, xcut, 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, ycut, ycut, 1.0, 1.0, 0.0]
    poly = iplt.Polygon(zip(x, y), ec='k', fc='none', clip_on=False,
                        transform=ax.transAxes, zorder=3)
    rect = iplt.Rectangle((xcut, 0.0), 1-xcut, ycut, ec='w', fc='w',
                          clip_on=False, transform=ax.transAxes, zorder=-1)
    tsax.add_patch(poly)
    tsax.add_patch(rect)
    prepare_map_axes(ax, extent=extent)
    prepare_ts_axes(tsax, dt=dt, mis=mis)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax1, cax2, tsax


def subplots_fancy(extent='1609', t=0.0, figsize=(192.0, 108.0)):
    """Init figure with fullscreen map and transparent time series."""
    figw, figh = figsize
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               gridspec_kw=dict(left=0.0, right=0.0,
                                                bottom=0.0, top=0.0))
    tsax = fig.add_axes([12.0/figw, 3.0/figh, 1-24.0/figw, 12.0/figh])
    ax.outline_patch.set_ec('none')
    tsax.set_facecolor('none')
    tsax.add_patch(plt.Rectangle((0.0, 0.0), 1.0, 20.0/figh,
                                 ec='w', fc='w', alpha=0.5, zorder=-1,
                                 clip_on=False, transform=ax.transAxes))
    prepare_map_axes(ax, extent=extent)
    return fig, ax, tsax


# Multi map subplot helpers
# --------------------------

def subplots_6(extent='alps'):
    """Init figure with six subplot."""
    figw, figh = 177.0, 85.0
    fig, grid = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                                 nrows=2, ncols=3, sharex=True, sharey=True,
                                 gridspec_kw=dict(left=1.5, right=1.5,
                                                  bottom=1.5, top=6.0,
                                                  hspace=1.5, wspace=1.5))
    for ax, l in zip(grid.flat, 'abcdef'):
        prepare_map_axes(ax, extent=extent)
        add_subfig_label('(%s)' % l, ax=ax)
    return fig, grid


def subplots_6_cax(extent='alps'):
    """Init figure with six subplot and colorbar inset."""
    fig, grid = subplots_6()
    figw, figh = fig.get_size_inches()*25.4
    cax = fig.add_axes([0.5-10.0/figw, 10.5/figh, 20.0/figw, 2.5/figh])
    return fig, grid, cax


def subplots_inputs(extent='alps', mode='vertical'):

    # initialize figure
    figw, figh = 177.0, 142.5 if mode == 'horizontal' else 102.0
    fig = iplt.figure_mm(figsize=(figw, figh))

    # prepare two grids in horizontal mode
    if mode == 'horizontal':
        grid1 = fig.subplots_mm(nrows=1, ncols=3, squeeze=False,
                                gridspec_kw=dict(left=1.5, right=1.5,
                                                 bottom=103.0, top=1.5,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm))
        grid2 = fig.subplots_mm(nrows=2, ncols=3, squeeze=False,
                                gridspec_kw=dict(left=1.5, right=1.5,
                                                 bottom=12.0, top=53.0,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm))

    # prepare two grids in vertical mode
    else:
        grid1 = fig.subplots_mm(nrows=3, ncols=1, squeeze=False,
                                gridspec_kw=dict(left=1.5, right=127.5,
                                                 bottom=1.5, top=1.5,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm)).T
        grid2 = fig.subplots_mm(nrows=3, ncols=2, squeeze=False,
                                gridspec_kw=dict(left=64.5, right=15.0,
                                                 bottom=1.5, top=1.5,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm)).T

    # merge axes grids
    grid = np.concatenate((grid1, grid2))

    # add colorbar axes
    for ax in grid[[0, 2], :].flat:
        pos = ax.get_position()
        if mode == 'horizontal':
            rect = [pos.x0, pos.y0-4.5/figh, pos.x1-pos.x0, 3.0/figh]
        else:
            rect = [pos.x1+1.5/figw, pos.y0, 3.0/figw, pos.y1-pos.y0]
        ax.cax = fig.add_axes(rect)

    # prepare axes
    for ax, l in zip(grid.flat, 'abcdfhegi'):
        prepare_map_axes(ax, extent=extent)
        add_subfig_label('(%s)' % l, ax=ax)

    # return figure and axes
    return fig, grid


def subplots_profiles(regions, labels):
    figw, figh = 177.0, 168.0
    nrows = len(regions)
    fig = iplt.figure_mm(figsize=(figw, figh))
    grid = fig.subplots_mm(nrows=nrows, ncols=1, sharex=False, sharey=False,
                           gridspec_kw=dict(left=1.5, right=figw-36.5,
                                            bottom=9.0, top=1.5,
                                            hspace=1.5, wspace=1.5),
                           subplot_kw=dict(projection=utm))
    tsgrid = fig.subplots_mm(nrows=nrows, ncols=1, sharex=True, sharey=False,
                             gridspec_kw=dict(left=38.0, right=12.0,
                                              bottom=9.0, top=1.5,
                                              hspace=1.5, wspace=1.5))
    for i, reg in enumerate(regions):
        ax = grid[i]
        tsax = tsgrid[i]
        prepare_map_axes(ax, extent=reg)
        plot_mis(tsax, y=(0.15 if i == nrows-1 else None))
        add_subfig_label('(%s)' % 'acegik'[i], ax=ax)
        add_subfig_label('(%s) ' % 'bdfhjl'[i] + labels[i], ax=tsax)
    return fig, grid, tsgrid


def subplots_trimlines(extent='valais', mode='column'):

    # initialize figure
    figw, figh = (177.0, 59.0) if mode == 'page' else (85.0, 115.0)
    fig = iplt.figure_mm(figsize=(figw, figh))

    # add axes in page mode
    if mode == 'page':
        ax = fig.add_axes([1.5/figw, 1.5/figh, 84.0/figw, 56.0/figh],
                          projection=utm)
        cax = fig.add_axes([12.0/figw, 53.0/figh, 30.0/figw, 3.0/figh])
        scax = fig.add_axes([103.0/figw, 9.0/figh, 48.5/figw, 48.5/figh])
        hsax = fig.add_axes([153.0/figw, 9.0/figh, 12.0/figw, 48.5/figh])

    # add axes in column mode
    else:
        ax = fig.add_axes([0.5/figw, 0.5/figh, 84.0/figw, 56.0/figh],
                          projection=utm)
        cax = fig.add_axes([12.0/figw, 52.0/figh, 30.0/figw, 3.0/figh])
        scax = fig.add_axes([11.75/figw, 65.5/figh, 48.0/figw, 48.0/figh])
        hsax = fig.add_axes([61.25/figw, 65.5/figh, 12.0/figw, 48.0/figh])

    # prepare map axes
    prepare_map_axes(ax, extent=extent)

    # add subfigure labels
    add_subfig_label('(a)', ax=scax)
    add_subfig_label('(b)', ax=hsax)
    add_subfig_label('(c)', ax=ax)

    # return figure and axes
    return fig, ax, cax, scax, hsax


# Text annotations
# ----------------

def add_colorbar(mappable, cax=None, ax=None, fig=None, label=None, **kw):
    """Add colorbar with auto orientation."""

    # try to figure out orientation
    orientation = kw.pop('orientation', None)
    if orientation is None and cax is not None:
        fig = cax.figure
        pos = cax.get_position().transformed(fig.dpi_scale_trans.inverted())
        ratio = abs(pos.height/pos.width)
        orientation = 'horizontal' if ratio < 1.0 else 'vertical'

    # find figure
    if fig is None:
        if cax is not None:
            fig = cax.figure
        elif ax is not None:
            fig = ax.figure
        else:
            fig = plt.gcf()

    # add colorbar
    cb = fig.colorbar(mappable, cax, orientation=orientation, **kw)

    # return colorbar
    return cb


def add_corner_tag(text, ax=None, ha='right', va='top', offset=2.5/25.4):
    """Add text in figure corner."""
    return add_subfig_label(text, ax=ax, ha=ha, va=va, offset=offset)


def add_subfig_label(text, ax=None, x=None, y=None, ha='left', va='top',
                     offset=2.5/25.4):
    """Add figure label in bold."""
    ax = ax or iplt.gca()
    x = x or (ha == 'right')  # 0 for left edge, 1 for right edge
    y = y or (va == 'top')  # 0 for bottom edge, 1 for top edge
    xoffset = (1 - 2*x)*offset
    yoffset = (1 - 2*y)*offset
    offset = mtransforms.ScaledTranslation(
        xoffset, yoffset, ax.figure.dpi_scale_trans)
    return ax.text(x, y, text, ha=ha, va=va, fontweight='bold',
                   transform=ax.transAxes + offset)


def add_signature(text, fig=None, offset=2.5/25.4):
    """Add signature for animations."""
    fig = fig or iplt.gcf()
    figw, figh = fig.get_size_inches()
    fig.text(1-offset/figw, offset/figh, text, ha='right', va='bottom')


# Map elements
# ------------


def draw_major_cities(ax=None, maxrank=5, textoffset=2, lang='en',
                      request=None):
    """Add major city locations with names."""
    shp = cshp.Reader(cshp.natural_earth(resolution='10m',
                                         category='cultural',
                                         name='populated_places'))
    for rec in shp.records():
        name = rec.attributes['name_'+lang].decode('utf8')
        rank = rec.attributes['SCALERANK']
        lon = rec.geometry.x
        lat = rec.geometry.y
        if rank <= maxrank or name in request:
            xc, yc = ax.projection.transform_point(lon, lat, src_crs=ll)
            xloc = 'r'  # ('l' if xc < center[0] else 'r')
            yloc = 'u'  # ('l' if yc < center[1] else 'u')
            dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
            dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
            ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
            va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
            ax.plot(xc, yc, marker='o', color='0.25', ms=2)
            ax.annotate(name, xy=(xc, yc), xytext=(dx, dy), color='0.25',
                        textcoords='offset points', ha=ha, va=va, clip_on=True)


def draw_cpu_grid(ax=None, extent='alps', nx=24, ny=24):
    """Add CPU partition grid."""
    ax = ax or iplt.gca()
    w, e, s, n = regions[extent]
    x = np.linspace(w, e, 24)
    y = np.linspace(s, n, 24)
    xx, yy = np.meshgrid(x, y)
    vlines = list(np.array([xx, yy]).T)
    hlines = list(np.array([xx.T, yy.T]).T)
    lines = hlines + vlines
    props = dict(color='k', linewidths=0.25, linestyles=':')
    lcoll = mcollections.LineCollection(lines, **props)
    ax.add_collection(lcoll)


def draw_natural_earth(ax=None, rivers=True, lakes=True, coastline=True,
                       countries=False, graticules=True):
    """Add Natural Earth geographic data vectors."""
    ax = ax or iplt.gca()
    if rivers:
        ax.add_feature(ne_rivers, zorder=0)
    if lakes:
        ax.add_feature(ne_lakes, zorder=0)
    if coastline:
        ax.add_feature(ne_coastline, zorder=0)
    if countries:
        ax.add_feature(ne_countries, zorder=0)
    if graticules:
        ax.add_feature(ne_graticules)


def draw_natural_earth_color(ax=None, rivers=True, lakes=True, coastline=True,
                             countries=False, graticules=True):
    """Add Natural Earth geographic data color vectors."""
    ax = ax or iplt.gca()
    if rivers:
        ax.add_feature(ne_rivers_color, zorder=0)
    if lakes:
        ax.add_feature(ne_lakes_color, zorder=0)
    if coastline:
        ax.add_feature(ne_coastline_color, zorder=0)
    if countries:
        ax.add_feature(ne_countries_color, zorder=0)
    if graticules:
        ax.add_feature(ne_graticules_color)


def draw_swisstopo_hydrology(ax=None, ec='#0978ab', fc='#c6ecff', lw=0.25):

    # get axes if None provided
    ax = ax or plt.gca()

    # draw swisstopo rivers
    filename = '../data/external/25_DKM500_GEWAESSER_LIN.shp'
    shp = cshp.Reader(filename)
    for rec in shp.records():
        symb = rec.attributes['Symbol']
        geom = rec.geometry
        if symb != '':
            lw = float(re.sub('[^0-9\.]', '', symb))
            ax.add_geometries(geom, swissplus, lw=lw,
                              edgecolor=ec, facecolor='none', zorder=0)

    # draw swisstopo lakes
    filename = '../data/external/22_DKM500_GEWAESSER_PLY.shp'
    shp = cshp.Reader(filename)
    ax.add_geometries(shp.geometries(), swissplus, lw=0.25,
                      edgecolor=ec, facecolor=fc, zorder=0)


def draw_lgm_outline(ax=None, c='#e31a1c'):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or iplt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=0.75,
                      edgecolor=c, facecolor='none')
    del shp


def draw_trimlines(ax=None, c=palette['darkblue'], s=4**2, alpha=0.75):
    """Add trimline locations."""
    ax = ax or iplt.gca()
    trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                              dtype=None, delimiter=',', names=True)
    ax.scatter(trimlines['x'], trimlines['y'], c=c, s=s, alpha=alpha,
               transform=swiss)


def draw_glacier_names(ax=None):
    """Add glacier lobes and ice cap names."""
    shp = cshp.Reader('../data/native/alpcyc_glacier_names.shp')
    for rec in shp.records():
        name = rec.attributes['name'].decode('utf-8').replace(' ', '\n')
        sort = rec.attributes['type']
        lon = rec.geometry.x
        lat = rec.geometry.y
        x, y = ax.projection.transform_point(lon, lat, src_crs=ll)
        style = ('italic' if sort == 'cap' else 'normal')
        ax.text(x, y, name, fontsize=6, style=style, ha='center', va='center')


def draw_ice_domes(ax=None, textoffset=4):
    """Add ice domes."""
    shp = cshp.Reader('../data/native/alpcyc_ice_domes.shp')
    for rec in shp.records():
        name = rec.attributes['name'].decode('utf-8')
        lon = rec.geometry.x
        lat = rec.geometry.y
        x, y = ax.projection.transform_point(lon, lat, src_crs=ll)
        ax.plot(x, y, 'k^', ms=6, mew=0)
        ax.annotate(name, xy=(x, y), xytext=(0, -textoffset), style='italic',
                    textcoords='offset points', ha='center', va='top')



def draw_major_transfluences(ax=None, textoffset=4):
    """Add major transfluences."""
    locations = {u'Col de Montgenèvre': 'lc',
                 u'Col du Mont-Cenis': 'uc',
                 u'Simplon Pass': 'uc',
                 u'Brünig Pass': 'uc',
                 u'Fern Pass': 'cl',
                 u'Seefeld Saddle': 'cr',
                 u'Gailberg Saddle': 'cl',
                 u'Kreuzberg Saddle': 'cr',
                 u'Kronhofer Törl': 'cl',
                 u'Stutenbodenalm': 'cr',
                 u'Pyhrn Pass': 'lc'}
    shp = cshp.Reader('../data/native/alpcyc_transfluences.shp')
    for rec in shp.records():
        name = rec.attributes['name'].decode('utf-8')
        if name in locations:
            lon = rec.geometry.x
            lat = rec.geometry.y
            x, y = ax.projection.transform_point(lon, lat, src_crs=ll)
            xloc = locations[name][1]
            yloc = locations[name][0]
            dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
            dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
            ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
            va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
            name = name.replace('Col de ', '')
            name = name.replace('Col du ', '')
            name = name.replace(' Alp', '')
            name = name.replace(' Pass', '')
            name = name.replace(' Saddle', '')
            # azim = rec.attributes['azimuth']
            ax.plot(x, y, 'kP', ms=6, mew=0)  # or marker=(2, 0, -azim)
            ax.annotate(name, xy=(x, y), xytext=(dx, dy),
                        textcoords='offset points', ha=ha, va=va)


def draw_boot_topo(ax=None, res='1km'):
    """Add bootstrapping topography image."""
    ax = ax or iplt.gca()
    nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-%s.nc' % res)
    im = nc.imshow('topg', ax, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    nc.close()
    return im


def draw_model_domain(ax=None, extent='alps'):
    """Add Rhine lobe scaling domain."""
    w, e, s, n = regions[extent]
    x = [w, e, e, w, w]
    y = [s, s, n, n, s]
    ax.plot(x, y, c='k', lw=0.5)

# Alps flow map elements
# ----------------------

def draw_alpflo_ice_divides(ax=None):
    """Add plotted ice divides."""
    ax = ax or iplt.gca()
    shp = cshp.Reader('../data/native/alpflo_ice_divides.shp')
    for rec in shp.records():
        rank = rec.attributes['rank']
        ax.add_geometries(shp.geometries(), ll, lw=2.0-0.5*rank, alpha=0.75,
                          edgecolor=palette['darkorange'],
                          facecolor='none')
    del shp


def draw_alpflo_water_divides(ax=None):
    """Add plotted water divides."""
    ax = ax or iplt.gca()
    shp = cshp.Reader('../data/native/alpflo_water_divides.shp')
    for rec in shp.records():
        ax.add_geometries(shp.geometries(), ll, lw=1.0, alpha=0.75,
                          edgecolor=palette['darkorange'],
                          facecolor='none', linestyles=[(0, [3, 1])])
    del shp


def draw_alpflo_cross_divides(ax=None, textoffset=4, strip=True):
    """Add crosswise divides."""
    shp = cshp.Reader('../data/native/alpflo_cross_divides.shp')
    c = palette['darkbrown']
    for rec in shp.records():
        lon = rec.geometry.x
        lat = rec.geometry.y
        xi, yi = ax.projection.transform_point(lon, lat, src_crs=ll)
        name = rec.attributes['name'].decode('utf-8')
        azim = rec.attributes['azimuth']
        xloc = 'l'
        yloc = 'u'
        dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
        dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
        ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
        va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
        ax.text(xi, yi, '$\Leftrightarrow$', fontsize=8, color=c,
                ha='center', va='center', rotation=90-azim)
        ax.annotate(name, xy=(xi, yi), xytext=(dx, dy), fontsize=4,
                    textcoords='offset points', ha=ha, va=va, color=c,
                    bbox=dict(ec=c, fc='w', pad=0.5, alpha=0.75))
    del shp


def draw_alpflo_transfluences(ax=None, textoffset=4, strip=True):
    """Add major transfluences."""
    shp = cshp.Reader('../data/native/alpflo_transfluences.shp')
    c = palette['darkpurple']
    for rec in shp.records():
        lon = rec.geometry.x
        lat = rec.geometry.y
        xi, yi = ax.projection.transform_point(lon, lat, src_crs=ll)
        name = rec.attributes['name'].decode('utf-8')
        alti = rec.attributes['altitude']
        azim = rec.attributes['azimuth']
        label = '%s, %s m' % (name, alti)
        xloc = 'r'
        yloc = 'l'
        dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
        dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
        ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
        va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
        ax.text(xi, yi, '$\Rightarrow$', fontsize=8, color=c,
                ha='center', va='center', rotation=90-azim)
        ax.annotate(label, xy=(xi, yi), xytext=(dx, dy), fontsize=4,
                    textcoords='offset points', ha=ha, va=va, color=c,
                    bbox=dict(ec=c, fc='w', pad=0.5, alpha=0.75))
    del shp


def draw_alpflo_glacier_names(ax=None):
    """Add glacier lobes and ice cap names."""
    shp = cshp.Reader('../data/native/alpflo_glacier_names.shp')
    for rec in shp.records():
        name = rec.attributes['name'].decode('utf-8').replace(' ', '\n')
        sort = rec.attributes['type']
        lon = rec.geometry.x
        lat = rec.geometry.y
        x, y = ax.projection.transform_point(lon, lat, src_crs=ll)
        style = ('italic' if sort == 'cap' else 'normal')
        ax.text(x, y, name, fontsize=6, style=style, ha='center', va='center')


def draw_fancy_map(ax=None, t=0, density=(12.8, 7.2), bg=True):
    """Fancy visualization of model results using high-res SRTM."""

    # get current axes if none
    ax = ax or plt.gca()
    axe = ax.get_extent()

    # prepare axes coordinates
    fig = ax.figure
    bbox = ax.get_window_extent()
    axx, axy = ut.pl.coords_from_extent(axe, *fig.get_size_inches()*fig.dpi)

    # estimate sea level drop
    nc = ut.io.load('input/dsl/specmap.nc')
    dsl = np.interp(t, nc.variables['time'][:], nc.variables['delta_SL'][:])
    nc.close()

    # load SRTM bedrock topography
    srb, sre = ut.io.open_gtif('../data/external/srtm.tif', extent=axe)
    srx, sry = ut.pl.coords_from_extent(sre, *srb.shape[::-1])

    # substract glacier thicknesses
    thk, the = ut.io.open_gtif('../data/external/thk.tif', extent=axe)
    assert the == sre
    srb -= thk

    # load boot topo
    filepath = 'input/boot/alps-srtm+thk+gou11simi-1km.nc'
    nc = ut.io.load(filepath)
    bref = nc.variables['topg'][:].T
    nc.close()

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)
    ncx, ncy, ncb = nc._extract_xyz('topg', t)
    ncx, ncy, ncs = nc._extract_xyz('usurf', t)

    # compute bedrock uplift
    ncu = ncb - bref

    # select interpolation coordinates
    xi, yi, ei = axx, axy, axe

    # interpolate surfaces to axes coords (interp2d seem faster than interp)
    bi = sinterp.interp2d(srx, sry, srb, kind='quintic')(xi, yi)
    si = sinterp.interp2d(ncx, ncy, ncs, kind='quintic')(xi, yi)
    mi = sinterp.interp2d(ncx, ncy, ncs.mask, kind='quintic')(xi, yi)
    ui = sinterp.interp2d(ncx, ncy, ncu, kind='quintic')(xi, yi)

    # correct basal topo for uplift and pop nunataks
    bi = bi + ui
    mi = (mi > 0.5) + (si < bi)
    si = np.ma.masked_array(si, mi)

    # if background map was requested
    if bg == True:

        # compute relief shading
        kw = dict(extent=ei, altitude=30.0, transparent=True)
        s300 = ut.pl.shading(bi, azimuth=300.0, **kw)
        s315 = ut.pl.shading(bi, azimuth=315.0, **kw)
        s330 = ut.pl.shading(bi, azimuth=330.0, **kw)
        sh = (s300+s315+s330) / 3.0

        # plot basal topography
        im = ax.imshow(bi, extent=ei, vmin=dsl-3e3, vmax=dsl+3e3,
                       cmap=icm.topo, zorder=-1)
        im = ax.imshow(sh, extent=ei, vmin=-1.0, vmax=1.0, cmap=shinemap,
                       zorder=-1)
        if bi.min() < 0.0:
            cs = ax.contour(bi, extent=ei, levels=[dsl], colors='#0978ab',
                            linestyles='dashed', linewidths=0.25)

    # plot surface topofraphy
    cs = ax.contourf(xi, yi, mi, levels=[0.0, 0.5], colors='w', alpha=0.75)
    cs = ax.contour(xi, yi, mi, levels=[0.5], colors='0.25', linewidths=0.25)
    cs = ax.contour(xi, yi, si, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
    cs = ax.contour(xi, yi, si, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)

    # add streamplot (not enough data result in ValueError)
    try:
        ss = nc.streamplot('velsurf', ax, t, cmap='Blues', norm=ut.pl.velnorm,
                           density=density, linewidth=0.5, arrowsize=0.25)
    except ValueError:
        pass

    # close extra data
    nc.close()


# Timeseries elements
# -------------------

def plot_multicolor(x, y, levels, colors, ax=None):
    """Plot using multiple colors along curve."""
    ax = ax or iplt.gca()
    bounds = [0] + [(abs(x-l)).argmin() for l in levels] + [-1]
    for i, c in enumerate(colors):
        imin = bounds[i]
        imax = bounds[i+1]
        ax.plot(x[imin:imax], y[imin:imax], c=c, lw=2.0)


def plot_mis(ax=None, y=1.075):
    """Plot MIS stages."""
    # source: http://www.lorraine-lisiecki.com/LR04_MISboundaries.txt.

    # prepare blended transform
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)

    # add spans
    kwa = dict(fc='0.9', lw=0.25, zorder=0)
    ax.axvspan(71, 57, **kwa)
    ax.axvspan(29, 14, **kwa)

    # add text
    if y is not None:
        kwa = dict(ha='center', va='center', transform=trans)
        ax.text((120+71)/2, y, 'MIS 5', **kwa)
        ax.text((71+57)/2, y, 'MIS 4', **kwa)
        ax.text((57+29)/2, y, 'MIS 3', **kwa)
        ax.text((29+14)/2, y, 'MIS 2', **kwa)
        ax.text((14+0)/2, y, 'MIS 1', **kwa)


def plot_dt(ax=None, t=0.0):
    """Plot scaled temperature offset time-series."""
    ax = ax or iplt.gca()

    # load time series
    nc = ut.io.load('input/dt/epica3222cool1220.nc')
    age = -nc.variables['time'][:]/1e3
    dt = nc.variables['delta_T'][:]
    nc.close()

    # plot time series
    mask = age >= -t/1e3
    ax.plot(age[mask], dt[mask], c='0.25')
    ax.set_xlabel('model age (ka)')
    ax.set_ylabel('temperature offset (K)', color='0.25')
    ax.set_xlim(120.0, 0.0)
    ax.set_ylim(-17.5, 2.5)
    ax.grid(axis='y')
    ax.locator_params(axis='y', nbins=6)


def plot_dt_fancy(ax=None, t=0.0, t0=-120e3, t1=-0e3, lang='en'):
    """Plot scaled temperature offset time-series in fancy animations."""
    ax = ax or iplt.gca()
    c = '0.25'

    # load time series
    nc = ut.io.load('input/dt/epica3222cool1220.nc')
    age = -nc.variables['time'][:]
    dt = nc.variables['delta_T'][:]
    nc.close()

    # plot time series
    mask = age >= -t
    ax.plot(age[mask], dt[mask], c=c)
    ax.text(-t, dt[mask][-1], '  % d' % round(dt[mask][-1]),
            color=c, ha='left', va='center', clip_on=True)

    # language-dependent labels
    lx = dict(en=u'{:,d} years ago',
              fr=u'il y a {:,d} ans')[lang].format(0-t).replace(',', r'$\,$')
    ly = dict(en=u'temperature\nchange (°C)',
              fr=u'écart (°C) de\ntempérature')[lang]

    # color axes spines
    for k, v in ax.spines.iteritems():
        v.set_color(c if k == 'left' else 'none')

    # set axes properties
    ax.set_xlim(-t0, -t1)
    ax.set_ylim(-17.5, 2.5)
    ax.set_yticks([-15.0, 0.0])
    ax.set_ylabel(ly, color=c, labelpad=-1)
    ax.tick_params(axis='x', colors=c)
    ax.tick_params(axis='y', colors=c)

    # add moving cursor and adaptive ticks
    ax.axvline(-t, c=c, lw=0.5)
    ax.set_xticks([-t0, -t, -t1])
    rt = 1.0*(t-t0)/(t1-t0)  # relative cursor position
    l0 = r'{:,d}'.format(0-t0).replace(',', r'$\,$')
    l1 = r'{:,d}'.format(0-t1).replace(',', r'$\,$')
    ax.set_xticklabels([l0*(rt>=1/12.0), lx, l1*(rt<=11/12.0)])
    ax.xaxis.tick_top()


def plot_slvol(ax=None, t=0.0):
    """Plot ice volume time-series."""
    ax = ax or iplt.gca()

    # load time series
    filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # print age of max volume
    #print age[vol.argmax()], vol.max()

    # plot time series
    mask = age >= -t/1e3
    ax.plot(age[mask], vol[mask], c=ut.pl.palette['darkblue'])
    ax.set_ylabel('ice volume (m s.l.e.)', color=ut.pl.palette['darkblue'])
    ax.set_xlim(120.0, 0.0)
    ax.set_ylim(-0.05, 0.35)
    ax.locator_params(axis='y', nbins=6)


def plot_slvol_fancy(ax=None, t=0.0, lang='en'):
    """Plot ice volume time-series for fancy animations."""
    ax = ax or iplt.gca()
    c = ut.pl.palette['darkblue']

    # load time series
    filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(365*24*60*60)
    vol = nc.variables['slvol'][:]*100.0
    nc.close()

    # plot time series
    mask = age >= -t
    ax.plot(age[mask], vol[mask], c=c)
    ax.text(age[mask][-1], vol[mask][-1], '  % d' % round(vol[mask][-1]),
            color=c, ha='left', va='center', clip_on=True)

    # language labels
    ly = dict(en=u'ice volume\n(cm sea level)',
              fr=u'vol. de glace\n(cm niv. marin)')[lang]

    # color axes spines
    for k, v in ax.spines.iteritems():
        v.set_color(c if k == 'right' else 'none')

    # set axes properties
    ax.set_ylim(-5.0, 35.0)
    ax.set_yticks([0.0, 30.0])
    ax.set_ylabel(ly, color=c)
    #ax.text(0.02, -0.05, ly, color=c, transform=ax.transAxes)
    ax.tick_params(axis='y', colors=c)


# Saving figures
# --------------

def savefig(fig=None):
    """Save figure to script filename."""
    fig = fig or plt.gcf()
    res = fig.savefig(os.path.splitext(sys.argv[0])[0])
    return res
