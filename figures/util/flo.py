# Copyright (c) 2017--2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Alps transfluence flow paper utils.
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp

LONLAT = ccrs.PlateCarree()


def draw_cross_divides(ax=None, textoffset=4, strip=True):
    """Add crosswise divides."""
    shp = cshp.Reader('../data/native/alpflo_cross_divides.shp')
    c = plt.get_cmap('Paired').colors[11]  # 'C11' is not a valid name
    for rec in shp.records():
        lon = rec.geometry.x
        lat = rec.geometry.y
        xi, yi = ax.projection.transform_point(lon, lat, src_crs=LONLAT)
        name = rec.attributes['name']
        azim = rec.attributes['azimuth']
        xloc = 'l'
        yloc = 'u'
        dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
        dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
        ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
        va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
        ax.text(xi, yi, r'$\Leftrightarrow$', fontsize=8, color=c,
                ha='center', va='center', rotation=90-azim)
        ax.annotate(name, xy=(xi, yi), xytext=(dx, dy), fontsize=4,
                    textcoords='offset points', ha=ha, va=va, color=c,
                    bbox=dict(ec=c, fc='w', pad=0.5, alpha=0.75))
    del shp


def draw_glacier_names(ax=None):
    """Add glacier lobes and ice cap names."""
    shp = cshp.Reader('../data/native/alpflo_glacier_names.shp')
    for rec in shp.records():
        name = rec.attributes['name'].replace(' ', '\n')
        sort = rec.attributes['type']
        lon = rec.geometry.x
        lat = rec.geometry.y
        x, y = ax.projection.transform_point(lon, lat, src_crs=LONLAT)
        style = ('italic' if sort == 'cap' else 'normal')
        ax.text(x, y, name, fontsize=6, style=style, ha='center', va='center')


def draw_ice_divides(ax=None):
    """Add plotted ice divides."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/alpflo_ice_divides.shp')
    for rec in shp.records():
        rank = rec.attributes['rank']
        ax.add_geometries(shp.geometries(), LONLAT, lw=2.0-0.5*rank,
                          alpha=0.75, edgecolor='C7', facecolor='none')
    del shp


def draw_transfluences(ax=None, textoffset=4, strip=True):
    """Add major transfluences."""
    shp = cshp.Reader('../data/native/alpflo_transfluences.shp')
    c = 'C9'
    for rec in shp.records():
        lon = rec.geometry.x
        lat = rec.geometry.y
        xi, yi = ax.projection.transform_point(lon, lat, src_crs=LONLAT)
        name = rec.attributes['name']
        alti = rec.attributes['altitude']
        azim = rec.attributes['azimuth']
        label = '%s, %s m' % (name, alti)
        xloc = 'r'
        yloc = 'l'
        dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
        dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
        ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
        va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
        ax.text(xi, yi, r'$\Rightarrow$', fontsize=8, color=c,
                ha='center', va='center', rotation=90-azim)
        ax.annotate(label, xy=(xi, yi), xytext=(dx, dy), fontsize=4,
                    textcoords='offset points', ha=ha, va=va, color=c,
                    bbox=dict(ec=c, fc='w', pad=0.5, alpha=0.75))
    del shp


def draw_water_divides(ax=None):
    """Add plotted water divides."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/alpflo_water_divides.shp')
    for rec in shp.records():
        ax.add_geometries(shp.geometries(), LONLAT, lw=1.0, alpha=0.75,
                          edgecolor='C7',
                          facecolor='none', linestyles=[(0, [3, 1])])
    del shp
