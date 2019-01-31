#!/usr/bin/env python2
# coding: utf-8

"""Native data plotting utils."""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp

# geographic projections
ll = ccrs.PlateCarree()
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)


# Map elements
# ------------

def draw_lgm_outline(ax=None, c='#e31a1c', alpha=0.75):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=alpha,
                      edgecolor=c, facecolor='none')
    del shp


def draw_trimlines(ax=None, c='C1', s=4**2, alpha=0.75):
    """Add trimline locations."""
    ax = ax or plt.gca()
    trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                              dtype=None, delimiter=',', names=True)
    ax.scatter(trimlines['x'], trimlines['y'], c=c, s=s, alpha=alpha,
               transform=swiss)


def draw_glacier_names(ax=None):
    """Add glacier lobes and ice cap names."""
    shp = cshp.Reader('../data/native/alpcyc_glacier_names.shp')
    for rec in shp.records():
        name = rec.attributes['name'].replace(' ', '\n')
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
        name = rec.attributes['name']
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
        name = rec.attributes['name']
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


# Alps flow map elements
# ----------------------

def draw_alpflo_ice_divides(ax=None):
    """Add plotted ice divides."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/alpflo_ice_divides.shp')
    for rec in shp.records():
        rank = rec.attributes['rank']
        ax.add_geometries(shp.geometries(), ll, lw=2.0-0.5*rank, alpha=0.75,
                          edgecolor='C7',
                          facecolor='none')
    del shp


def draw_alpflo_water_divides(ax=None):
    """Add plotted water divides."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/alpflo_water_divides.shp')
    for rec in shp.records():
        ax.add_geometries(shp.geometries(), ll, lw=1.0, alpha=0.75,
                          edgecolor='C7',
                          facecolor='none', linestyles=[(0, [3, 1])])
    del shp


def draw_alpflo_cross_divides(ax=None, textoffset=4, strip=True):
    """Add crosswise divides."""
    shp = cshp.Reader('../data/native/alpflo_cross_divides.shp')
    c = plt.get_cmap('Paired').colors[11]  # 'C11' is not a valid name
    for rec in shp.records():
        lon = rec.geometry.x
        lat = rec.geometry.y
        xi, yi = ax.projection.transform_point(lon, lat, src_crs=ll)
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


def draw_alpflo_transfluences(ax=None, textoffset=4, strip=True):
    """Add major transfluences."""
    shp = cshp.Reader('../data/native/alpflo_transfluences.shp')
    c = 'C9'
    for rec in shp.records():
        lon = rec.geometry.x
        lat = rec.geometry.y
        xi, yi = ax.projection.transform_point(lon, lat, src_crs=ll)
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


def draw_alpflo_glacier_names(ax=None):
    """Add glacier lobes and ice cap names."""
    shp = cshp.Reader('../data/native/alpflo_glacier_names.shp')
    for rec in shp.records():
        name = rec.attributes['name'].replace(' ', '\n')
        sort = rec.attributes['type']
        lon = rec.geometry.x
        lat = rec.geometry.y
        x, y = ax.projection.transform_point(lon, lat, src_crs=ll)
        style = ('italic' if sort == 'cap' else 'normal')
        ax.text(x, y, name, fontsize=6, style=style, ha='center', va='center')
