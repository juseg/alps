#!/usr/bin/env python2
# coding: utf-8

"""Natural Earth Data and Swisstopo hydrology."""

import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp
import cartowik.naturalearth as cne
import util as ut


# Geographic data
# ---------------

# geographic projections
ll = ccrs.PlateCarree()
swissplus = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=2600e3, false_northing=1200e3)


# Map elements
# ------------

def draw_natural_earth(ax=None, mode='gs', **kwargs):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.85' if mode == 'gs' else '#c6ecff'
    cne.add_rivers(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_lakes(ax=ax, edgecolor=edgecolor, facecolor=facecolor, zorder=0, **kwargs)
    cne.add_coastline(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_graticules(ax=ax, interval=1, **kwargs)


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
        x, y = ax.projection.transform_point(geom.x, geom.y, src_crs=ll)
        if west > x or x > east or south > y or y > north:
            continue

        # plot
        ax.plot(x, y, marker='o', color='0.25', ms=2)
        ax.annotate(name, xy=(x, y), xytext=(dx, dy), color='0.25',
                    textcoords='offset points', ha=ha, va=va, clip_on=True)


def draw_swisstopo_hydrology(ax=None, mode='gs', **kwargs):

    # get axes if None provided
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.85' if mode == 'gs' else '#c6ecff'

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
    w0, e0, s0, n0 = ut.fi.regions['anim_ch_1']

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
        draw_swisstopo_hydrology(alpha=alpha, **kwargs)
    if coverage < 1.0:
        draw_natural_earth(alpha=1-alpha, **kwargs)
