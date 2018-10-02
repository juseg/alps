#!/usr/bin/env python2
# coding: utf-8

"""Plotting functions."""

import os
import re
import sys
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.collections as mcollections
import util as ut

# Color palette
# -------------

# set color cycle to colorbrewer Paired palette
plt.rc('axes', prop_cycle=plt.cycler(color=plt.get_cmap('Paired').colors))

# personal colormaps
# FIXME move to util/cm
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
stereo = ccrs.Stereographic(central_latitude=0.0, central_longitude=7.5)


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
    return ut.fi.add_subfig_label(text, ax=ax, ha=ha, va=va, offset=offset)


def add_signature(text, fig=None, offset=2.5/25.4):
    """Add signature for animations."""
    fig = fig or plt.gcf()
    figw, figh = fig.get_size_inches()
    fig.text(1-offset/figw, offset/figh, text, ha='right', va='bottom')


# Map elements
# ------------


def draw_boot_topo(ax=None, filename='alpcyc.1km.in.nc'):
    """Add bootstrapping topography image."""
    ax = ax or plt.gca()
    with ut.io.open_dataset('../data/processed/'+filename) as ds:
        im = (ds.topg/1e3).plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                                       vmin=0.0, vmax=3.0, zorder=-1)
    return im


def draw_cpu_grid(ax=None, extent='alps', nx=24, ny=24):
    """Add CPU partition grid."""
    ax = ax or plt.gca()
    w, e, s, n = ut.fi.regions[extent]
    x = np.linspace(w, e, 24)
    y = np.linspace(s, n, 24)
    xx, yy = np.meshgrid(x, y)
    vlines = list(np.array([xx, yy]).T)
    hlines = list(np.array([xx.T, yy.T]).T)
    lines = hlines + vlines
    props = dict(color='k', linewidths=0.25, linestyles=':')
    lcoll = mcollections.LineCollection(lines, **props)
    ax.add_collection(lcoll)


def draw_lgm_outline(ax=None, c='#e31a1c'):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=0.75,
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


def draw_model_domain(ax=None, extent='alps'):
    """Add Rhine lobe scaling domain."""
    w, e, s, n = ut.fi.regions[extent]
    x = [w, e, e, w, w]
    y = [s, s, n, n, s]
    ax.plot(x, y, c='k', lw=0.5, transform=utm)

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
    c = 'C9'
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


# Saving figures
# --------------

def savefig(fig=None):
    """Save figure to script filename."""
    fig = fig or plt.gcf()
    res = fig.savefig(os.path.splitext(sys.argv[0])[0])
    return res
