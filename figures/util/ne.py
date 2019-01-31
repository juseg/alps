#!/usr/bin/env python2
# coding: utf-8

"""Natural Earth Data and Swisstopo hydrology."""

import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp
import cartowik.naturalearth as cne


# Geographic data
# ---------------

# geographic projections
ll = ccrs.PlateCarree()
swissplus = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=2600e3, false_northing=1200e3)


# Map elements
# ------------

def draw_natural_earth(ax=None, mode='gs'):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.85' if mode == 'gs' else '#c6ecff'
    cne.add_rivers(ax=ax, edgecolor=edgecolor, zorder=0)
    cne.add_lakes(ax=ax, edgecolor=edgecolor, facecolor=facecolor, zorder=0)
    cne.add_coastline(ax=ax, edgecolor=edgecolor, zorder=0)
    cne.add_graticules(ax=ax, interval=1)


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
            lw = float(re.sub(r'[^0-9\.]', '', symb))
            ax.add_geometries(geom, swissplus, lw=lw,
                              edgecolor=ec, facecolor='none', zorder=0)

    # draw swisstopo lakes
    filename = '../data/external/22_DKM500_GEWAESSER_PLY.shp'
    shp = cshp.Reader(filename)
    ax.add_geometries(shp.geometries(), swissplus, lw=0.25,
                      edgecolor=ec, facecolor=fc, zorder=0)
