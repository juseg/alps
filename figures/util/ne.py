#!/usr/bin/env python2
# coding: utf-8

"""Natural Earth Data and Swisstopo hydrology."""

import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp


# Geographic data
# ---------------

# geographic projections
ll = ccrs.PlateCarree()
swissplus = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=2600e3, false_northing=1200e3)

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


# Map elements
# ------------

def draw_natural_earth(ax=None, rivers=True, lakes=True, coastline=True,
                       countries=False, graticules=True):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
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


def draw_natural_earth_color(ax=None, rivers=True, lakes=True, coastline=True,
                             countries=False, graticules=True):
    """Add Natural Earth geographic data color vectors."""
    ax = ax or plt.gca()
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
            lw = float(re.sub(r'[^0-9\.]', '', symb))
            ax.add_geometries(geom, swissplus, lw=lw,
                              edgecolor=ec, facecolor='none', zorder=0)

    # draw swisstopo lakes
    filename = '../data/external/22_DKM500_GEWAESSER_PLY.shp'
    shp = cshp.Reader(filename)
    ax.add_geometries(shp.geometries(), swissplus, lw=0.25,
                      edgecolor=ec, facecolor=fc, zorder=0)
