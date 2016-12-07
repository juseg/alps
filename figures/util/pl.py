#!/usr/bin/env python2
# coding: utf-8

"""Plotting functions."""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp
import iceplotlib.plot as iplt
from matplotlib.transforms import ScaledTranslation


# color brewer Paired palette
colorkeys = [tone+hue
             for hue in ('blue', 'green', 'red', 'orange', 'purple', 'brown')
             for tone in ('light', 'dark')]
colorvals = iplt.get_cmap('Paired', 12)(range(12))
palette = dict(zip(colorkeys, colorvals))


# geographic projections
ll = ccrs.PlateCarree()
utm = ccrs.UTM(32)
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)


# cartopy features
rivers = cfeature.NaturalEarthFeature(
    category='physical', name='rivers_lake_centerlines', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.5)
lakes = cfeature.NaturalEarthFeature(
    category='physical', name='lakes', scale='10m',
    edgecolor='0.25', facecolor='0.85', lw=0.25)
coastline = cfeature.NaturalEarthFeature(
    category='physical', name='coastline', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.25)
graticules = cfeature.NaturalEarthFeature(
    category='physical', name='graticules_1', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.1)


# iceplotlib functions
subplots_mm = iplt.subplots_mm
get_cmap = iplt.get_cmap


def subplots_ts(nrows=1, ncols=1):
    """Init figure with margins adapted for simple timeseries."""
    figw, figh = 85.0, 30.0 + nrows*30.0
    return iplt.subplots_mm(nrows=nrows, ncols=ncols, figsize=(figw, figh),
                            sharex=True, sharey=False,
                            left=10.0, right=2.5, bottom=7.5, top=2.5,
                            hspace=2.5, wspace=2.5)


def subplots_cax():
    """Init figure with unique subplot and right colorbar."""
    figw, figh = 170.0, 105.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=17.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([1-15.0/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])
    ax.set_rasterization_zorder(2.5)
    return fig, ax, cax


def subplots_cax_inset():
    """Init figure with unique subplot and colorbar inset."""
    figw, figh = 170.0, 115.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=2.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([5.0/figw, 1-10.0/figh, 40.0/figw, 5.0/figh])
    ax.set_rasterization_zorder(2.5)
    return fig, ax, cax


def subplots_cax_ts(labels=True):
    """Init figure with subplot, side colorbar and timeseries."""
    figw, figh = 170.0, 145.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=17.5, bottom=42.5, top=2.5)
    cax = fig.add_axes([5.0/figw, 65.0/figh, 5.0/figw, 40.0/figh])
    tsax = fig.add_axes([12.5/figw, 10.0/figh, 1-22.5/figw, 30.0/figh])
    ax.set_rasterization_zorder(2.5)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax, tsax


def subplots_cax_ts_inset(labels=True):
    """Init figure with subplot, colorbar and timeseries insets."""
    figw, figh = 170.0, 115.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=2.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([5.0/figw, 65.0/figh, 5.0/figw, 40.0/figh])
    tsax = fig.add_axes([67.5/figw, 15.0/figh, 85.0/figw, 20.0/figh])
    ax.set_rasterization_zorder(2.5)
    rect = iplt.Rectangle((55.0/figw, 5.0/figh), 110.0/figw, 35.0/figh,
                          ec='k', fc='w', alpha=0.75, clip_on=False,
                          transform=fig.transFigure, zorder=-1)
    tsax.add_patch(rect)
    tsax.set_axis_bgcolor('none')
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax, tsax


def subplots_cax_ts_cut(labels=True):
    """Init figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 170.0, 115.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=2.5, bottom=2.5, top=2.5)
    cax = fig.add_axes([65.0/figw, 1-10.0/figh, 40.0/figw, 5.0/figh])
    tsax = fig.add_axes([70.0/figw, 10.0/figh, 87.5/figw, 22.5/figh])
    ax.set_rasterization_zorder(2.5)
    ax.outline_patch.set_ec('none')
    x = [0.0, 1/3., 1/3., 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, 1/3., 1/3., 1.0, 1.0, 0.0]
    poly = iplt.Polygon(zip(x, y), ec='k', fc='none', clip_on=False,
                        transform=ax.transAxes, zorder=3)
    rect = iplt.Rectangle((1/3., 0.0), 2/3., 1/3., ec='w', fc='w',
                            clip_on=False, transform=ax.transAxes, zorder=-1)
    tsax.add_patch(poly)
    tsax.add_patch(rect)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax, tsax


def add_subfig_label(text, ax=None, ha='left', va='top', offset=2.5/25.4):
    """Add figure label in bold."""
    ax = ax or plt.gca()
    x = (ha == 'right')  # 0 for left edge, 1 for right edge
    y = (va == 'top')  # 0 for bottom edge, 1 for top edge
    xoffset = (1 - 2*x)*offset
    yoffset = (1 - 2*y)*offset
    offset = ScaledTranslation(xoffset, yoffset, ax.figure.dpi_scale_trans)
    return ax.text(x, y, text, ha=ha, va=va, fontweight='bold',
                   transform=ax.transAxes + offset)


def draw_natural_earth(ax=None):
    """Add Natural Earth geographic data vectors."""
    ax = ax or iplt.gca()
    ax.add_feature(rivers, zorder=0)
    ax.add_feature(lakes, zorder=0)
    ax.add_feature(coastline, zorder=0)
    ax.add_feature(graticules)


def draw_lgm_outline(ax=None):
    """Add Ehlers et al. hole-filled LGM outline."""
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=0.75,
                      edgecolor='#e31a1c', facecolor='none', zorder=0)
    del shp
