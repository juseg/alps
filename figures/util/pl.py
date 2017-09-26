#!/usr/bin/env python2
# coding: utf-8

"""Plotting functions."""

import util as ut
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp
import iceplotlib.plot as iplt
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


# Mapping properties
# ------------------

# velocity norm
velnorm = mcolors.LogNorm(1e1, 1e3)

# contour levels
topolevs = range(0, 4000, 200)
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
stereo = ccrs.Stereographic(central_latitude=0.0, central_longitude=7.5)

# geographic regions
regions = {'alps': (150e3, 1050e3, 4820e3, 5420e3),    # model domain 900x600
           'bern': (390e3, 465e3, 5125e3, 5175e3),     # Bern 75x50
           'crop': (155e3, 1045e3, 4825e3, 5415e3),    # 5 km crop 895x895
           'guil': (230e3, 470e3, 5050e3, 5240e3),     # Guillaume 240x190
           'west': (250e3, 700e3, 4970e3, 5270e3),     # western 450x300
           'isere': (230e3, 370e3, 5000e3, 5100e3),    # Isère 140x100
           'ivrea': (300e3, 440e3, 5000e3, 5100e3),    # Ivrea 140x100
           'rhine': (410e3, 620e3, 5150e3, 5300e3),    # Rhine 210x150
           'rhone': (300e3, 475e3, 5100e3, 5225e3),    # Rhone 140x100 175x125
           'rhlobe': (450e3, 600e3, 5225e3, 5325e3),   # Rhine lobe 150x100
           'valais': (310e3, 460e3, 5065e3, 5165e3),   # Trimlines 150x100
           'aletsch': (414e3, 444e3, 5139e3, 5159e3)}  # Aletsch 30x20

# cartopy features
ne_rivers = cfeature.NaturalEarthFeature(
    category='physical', name='rivers_lake_centerlines', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.5)
ne_lakes = cfeature.NaturalEarthFeature(
    category='physical', name='lakes', scale='10m',
    edgecolor='0.25', facecolor='0.85', lw=0.25)
ne_coastline = cfeature.NaturalEarthFeature(
    category='physical', name='coastline', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.25)
ne_graticules = cfeature.NaturalEarthFeature(
    category='physical', name='graticules_1', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.1)


# Iceplotlib functions
# --------------------

figure = iplt.figure
subplots_mm = iplt.subplots_mm
get_cmap = iplt.get_cmap
close = iplt.close


# Figures and axes creation
# -------------------------

def prepare_axes(ax=None, tsax=None, extent='alps', labels=True,
                 dt=True, mis=True, t=0.0):
    """Prepare map and timeseries axes before plotting."""

    # prepare map axes
    if ax is not None:
        ax.set_rasterization_zorder(2.5)
        ax.set_extent(regions[extent], crs=ax.projection)

    # prepare timeseries axes
    if tsax is not None:
        if dt is True:
            plot_dt(tsax, t=t)
        if mis is True:
            plot_mis(tsax)

    # add subfigure labels
    if ax is not None and tsax is not None and labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)


def subplots_ts(nrows=1, ncols=1, figw=85.0):
    """Init figure with margins adapted for simple timeseries."""
    figh = 30.0 + nrows*30.0
    fig, grid = iplt.subplots_mm(nrows=nrows, ncols=ncols,
                                 figsize=(figw, figh),
                                 left=10.0, right=2.5, bottom=7.5, top=2.5,
                                 sharex=True, sharey=False,
                                 hspace=2.5, wspace=2.5)
    if nrows*ncols > 1:
        for ax, label in zip(grid, list('abcdef')):
            ut.pl.add_subfig_label('({})'.format(label), ax=ax)
    return fig, grid


def subplots_cax(extent='alps'):
    """Init figure with unique subplot and right colorbar."""
    figw, figh = 170.0, 105.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=17.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([1-15.0/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])
    prepare_axes(ax, extent=extent)
    return fig, ax, cax


def subplots_cax_inset(extent='alps'):
    """Init figure with unique subplot and colorbar inset."""
    figw, figh = 170.0, 115.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=2.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([5.0/figw, 65.0/figh, 5.0/figw, 40.0/figh])
    prepare_axes(ax, extent=extent)
    return fig, ax, cax


def subplots_cax_ts(extent='alps', labels=True, dt=True, mis=True):
    """Init figure with subplot, side colorbar and timeseries."""
    figw, figh = 170.0, 145.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=17.5, bottom=42.5, top=2.5)
    cax = fig.add_axes([1-15.0/figw, 42.5/figh, 5.0/figw, 100.0/figh])
    tsax = fig.add_axes([12.5/figw, 10.0/figh, 1-22.5/figw, 30.0/figh])
    prepare_axes(ax, tsax, extent, labels, dt, mis)
    return fig, ax, cax, tsax


def subplots_cax_ts_inset(extent='alps', labels=True, dt=True, mis=True):
    """Init figure with subplot, colorbar and timeseries insets."""
    figw, figh = 170.0, 115.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=2.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([5.0/figw, 65.0/figh, 5.0/figw, 40.0/figh])
    tsax = fig.add_axes([67.5/figw, 15.0/figh, 85.0/figw, 20.0/figh])
    rect = iplt.Rectangle((55.0/figw, 5.0/figh), 110.0/figw, 35.0/figh,
                          ec='k', fc='w', alpha=0.75, clip_on=False,
                          transform=fig.transFigure, zorder=-1)
    tsax.add_patch(rect)
    tsax.set_facecolor('none')
    prepare_axes(ax, tsax, extent, labels, dt, mis)
    return fig, ax, cax, tsax


def subplots_cax_ts_cut(extent='alps', labels=True, dt=True, mis=True):
    """Init figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 170.0, 115.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=2.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([5.0/figw, 65.0/figh, 5.0/figw, 40.0/figh])
    tsax = fig.add_axes([70.0/figw, 10.0/figh, 87.5/figw, 22.5/figh])
    ax.outline_patch.set_ec('none')
    x = [0.0, 1/3., 1/3., 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, 1/3., 1/3., 1.0, 1.0, 0.0]
    poly = iplt.Polygon(zip(x, y), ec='k', fc='none', clip_on=False,
                        transform=ax.transAxes, zorder=3)
    rect = iplt.Rectangle((1/3., 0.0), 2/3., 1/3., ec='w', fc='w',
                          clip_on=False, transform=ax.transAxes, zorder=-1)
    tsax.add_patch(poly)
    tsax.add_patch(rect)
    prepare_axes(ax, tsax, extent, labels, dt, mis)
    return fig, ax, cax, tsax


def subplots_cax_ts_anim(extent='alps', labels=False, dt=True, mis=True,
                         t=0.0):
    """Init figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 180.0, 120.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=0.0, right=0.0, bottom=0.0, top=0.0)
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
    prepare_axes(ax, tsax, extent, labels, dt, mis, t)
    return fig, ax, cax, tsax


def subplots_cax_ts_big(extent='crop', labels=False, dt=True, mis=True):
    """Init big figure with subplot, colorbar and timeseries insets."""
    # initialize figure
    figw, figh = 405.0, 270.0
    fig, ax = ut.pl.subplots_mm(figsize=(figw, figh), projection=ut.pl.utm,
                                left=2.5, right=2.5, bottom=2.5, top=2.5)
    cax1 = fig.add_axes([12.5/figw, 1-32.5/figh, 50.0/figw, 5.0/figh])
    cax2 = fig.add_axes([12.5/figw, 1-52.5/figh, 50.0/figw, 5.0/figh])
    tsax = fig.add_axes([157.5/figw, 27.5/figh, 205.0/figw, 40.0/figh])
    rect = iplt.Rectangle((142.5/figw, 12.5/figh), 250.0/figw, 75.0/figh,
                          ec='k', fc='w', alpha=1.0, clip_on=False,
                          transform=fig.transFigure, zorder=-1)
    tsax.add_patch(rect)
    tsax.set_facecolor('none')
    prepare_axes(ax, tsax, extent, labels, dt, mis)
    return fig, ax, cax1, cax2, tsax


# Text annotations
# ----------------

def add_corner_tag(text, ax=None, ha='right', va='top', offset=2.5/25.4):
    """Add text in figure corner."""
    return add_subfig_label(text, ax=ax, ha=ha, va=va, offset=offset)


def add_subfig_label(text, ax=None, ha='left', va='top', offset=2.5/25.4):
    """Add figure label in bold."""
    ax = ax or iplt.gca()
    x = (ha == 'right')  # 0 for left edge, 1 for right edge
    y = (va == 'top')  # 0 for bottom edge, 1 for top edge
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


def draw_major_cities(ax=None, maxrank=5, textoffset=4):
    """Add major city locations with names."""
    shp = cshp.Reader(cshp.natural_earth(resolution='10m',
                                         category='cultural',
                                         name='populated_places_simple'))
    for rec in shp.records():
        name = rec.attributes['name'].decode('latin-1')
        rank = rec.attributes['scalerank']
        pop = rec.attributes['pop_max']
        lon = rec.geometry.x
        lat = rec.geometry.y
        if rank <= maxrank:
            xc, yc = ax.projection.transform_point(lon, lat, src_crs=ut.pl.ll)
            xloc = 'r'  #('l' if xc < center[0] else 'r')
            yloc = 'u'  #('l' if yc < center[1] else 'u')
            dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
            dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
            ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
            va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
            ax.plot(xc, yc, 'ko')
            ax.annotate(name, xy=(xc, yc), xytext=(dx, dy),
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
                       graticules=True):
    """Add Natural Earth geographic data vectors."""
    ax = ax or iplt.gca()
    if rivers:
        ax.add_feature(ne_rivers, zorder=0)
    if lakes:
        ax.add_feature(ne_lakes, zorder=0)
    if coastline:
        ax.add_feature(ne_coastline, zorder=0)
    if graticules:
        ax.add_feature(ne_graticules)


def draw_lgm_outline(ax=None, c='#e31a1c'):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or iplt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=0.75,
                      edgecolor=c, facecolor='none', zorder=0)
    del shp


def draw_envelope(ax=None, levels=None, colors=None):
    """Add modelled maximum thickness surface elevation."""
    ax = ax or iplt.gca()
    maxthksrf, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxicesrf')
    if levels is not None or colors is not None:
        cs = ax.contourf(maxthksrf, levels, extent=extent, colors=colors,
                         extend='max', alpha=0.75)
    else:
        cs = None
    ax.contour(maxthksrf, ut.pl.inlevs, extent=extent, colors='0.25', linewidths=0.1)
    ax.contour(maxthksrf, ut.pl.utlevs, extent=extent, colors='0.25', linewidths=0.25)
    ax.contour(maxthksrf.mask, [0.5], extent=extent, colors='k', linewidths=0.5)
    return cs


def draw_footprint(ax=None):
    """Add modelled LGM footprint."""
    ax = ax or iplt.gca()
    run = '-'.join(ut.alpcyc_bestrun.rstrip('/').split('/')[-2:])
    shp = cshp.Reader('../data/processed/%s-footprint.shp' % run)
    ax.add_geometries(shp.geometries(), utm, lw=0.5, alpha=0.75,
                      edgecolor=palette['darkorange'], facecolor='none',
                      linestyles=[(0, [3, 1])], zorder=0)
    del shp


def draw_trimlines(ax=None, c=palette['darkblue'], s=4**2, alpha=0.75):
    """Add trimline locations."""
    ax = ax or iplt.gca()
    trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                              dtype=None, delimiter=',', names=True)
    ax.scatter(trimlines['x'], trimlines['y'], c=c, s=s, alpha=alpha,
               transform=ut.pl.swiss)


def draw_glacier_names(ax=None):
    """Add glacier lobes and ice cap names."""
    shp = cshp.Reader('../data/native/alpcyc_glacier_names.shp')
    for rec in shp.records():
        name = rec.attributes['name'].decode('utf-8').replace(' ', '\n')
        sort = rec.attributes['type']
        lon = rec.geometry.x
        lat = rec.geometry.y
        x, y = ax.projection.transform_point(lon, lat, src_crs=ut.pl.ll)
        style = ('italic' if sort == 'cap' else 'normal')
        ax.text(x, y, name, fontsize=6, style=style, ha='center', va='center')


def draw_boot_topo(ax=None, res='1km'):
    """Add bootstrapping topography image."""
    ax = ax or iplt.gca()
    nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-%s.nc' % res)
    im = nc.imshow('topg', ax, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    nc.close()
    return im


def draw_scaling_domain(ax=None):
    """Add Rhine lobe scaling domain."""
    w, e, s, n = ut.pl.regions['rhlobe']
    x = [w, e, e, w, w]
    y = [s, s, n, n, s]
    ax.plot(x, y, c='k', lw=0.5)

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
    nc = ut.io.load('input/dt/epica3222cool0950.nc')
    age = -nc.variables['time'][:]/1e3
    dt = nc.variables['delta_T'][:]
    nc.close()

    # plot time series
    mask = age>=-t/1e3
    ax.plot(age[mask], dt[mask], c='0.25')
    ax.set_xlabel('model age (ka)')
    ax.set_ylabel('temperature offset (K)', color='0.25')
    ax.set_xlim(120.0, 0.0)
    ax.set_ylim(-12.5, 7.5)
    ax.grid(axis='y')
    ax.locator_params(axis='y', nbins=6)
