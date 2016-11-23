#!/usr/bin/env python2
# coding: utf-8

"""Plotting functions."""

import iceplotlib.plot as iplt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# geographic projections
utm = ccrs.UTM(32)

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


def subplots_cax():
    """Init figure with unique subplot and right colorbar."""
    figw, figh = 135.0, 80.0
    fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                               left=2.5, right=20.0, bottom=2.5, top=2.5)
    cax = fig.add_axes([1-17.5/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])
    ax.set_rasterization_zorder(2.5)
    return fig, ax, cax


def draw_natural_earth(ax=None):
    """Add Natural Earth geographic data vectors."""
    ax = ax or iplt.gca()
    ax.add_feature(rivers, zorder=0)
    ax.add_feature(lakes, zorder=0)
    ax.add_feature(coastline, zorder=0)
    ax.add_feature(graticules)
