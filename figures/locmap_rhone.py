#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import iceplotlib.cm as icm
from netCDF4 import Dataset

# parameters
bwu = 0.5      # base width unit
scale = '10m'  # Natural Earth scale

# projections and boundaries
ll = ccrs.PlateCarree()
proj = ccrs.UTM(32)
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3)
w, e, s, n = 0e3, 1500e3, 4500e3, 5500e3  # etopo reprojection
w, e, s, n = 150e3, 1050e3, 4820e3, 5420e3  # full alps
w, e, s, n = 230e3, 470e3, 5050e3, 5240e3  # west alps 240x190 km
w, e, s, n = 172e3, 528e3, 5025e3, 5265e3  # west alps 356x240 km
w, e, s, n = 194.25e3-10e3, 505.75e3-10e3, 5040e3, 5250e3  # 311.5x210 km


# ETOPO1 background topo
def draw_etopo1(**kwargs):
    """Draw ETOPO1 background and coastline"""
    nc = Dataset('../data/external/etopo1-alps.nc')
    x = nc.variables['x']
    y = nc.variables['y']
    z = nc.variables['Band1']
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2 - (x[-1]-x[-2])/2  # weird but works
    n = (3*y[0]-y[1])/2
    s = (3*y[-1]-y[-2])/2 - (y[-1]-y[-2])/2  # weird but works
    ax = ax or plt.gca()
    im = ax.imshow(z, extent=(w, e, n, s),
                   cmap=icm.topo, norm=Normalize(-6e3, 6e3))
    cs = ax.contour(x[:], y[:], z[:], levels=[0],
                    colors='#0978ab', linewidths=0.5*bwu, zorder=0.5)
    nc.close()

# ETOPO1 background topo
def draw_srtm(ax=None, azimuth=315.0, altitude=30.0, exag=1.0):
    """Draw SRTM background"""

    # get axes if None provided
    ax = ax or plt.gca()

    # extract data
    nc = Dataset('../data/external/srtm-west.nc')
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    z = nc.variables['Band1'][:]
    nc.close()

    # get extent
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2

    # convert to rad from the x-axis
    azimuth = (90.0-azimuth)*np.pi / 180.
    altitude = altitude*np.pi / 180.

    # compute cartesian coords of the illumination direction
    xlight = np.cos(azimuth) * np.cos(altitude)
    ylight = np.sin(azimuth) * np.cos(altitude)
    zlight = np.sin(altitude)
    zlight = 0.0  # remove shades from horizontal surfaces

    # compute hillshade (dot product of normal and light direction vectors)
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    u, v = np.gradient(z*exag, dx, dy)
    shade = (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)

    # plot color map
    im = ax.imshow(z, extent=(w, e, s, n),
                   cmap=icm.topo, vmin=-6e3, vmax=6e3)

    # plot shadows only (white transparency is not possible)
    im = ax.imshow((shade>0)*shade, extent=(w, e, s, n),
                    cmap=icm.shades, vmin=0.0, vmax=1.0)

# Ehlers and Gibbard LGM
def draw_lgm_bini(ax=None):
    filename = ('/usr/itetnas01/data-vaw-01/glazioarch/GeoBaseData/Geology/'
                'GK500/LastGlacialMaximum/Data/LGM500_L.shp')
    shp = shpreader.Reader(filename)
    outlines = [rec.geometry for rec in shp.records()
                if rec.attributes['LineType'] == 'Outline']
    ax = ax or plt.gca()
    ax.add_geometries(outlines, swiss, alpha=0.75,
                      edgecolor='#800000', facecolor='none', lw=1.0*bwu)

def draw_lgm_ehlers(ax=None):
    filename = '../data/native/lgm_alpen_holefilled.shp'
    shp = shpreader.Reader(filename)
    ax = ax or plt.gca()
    ax.add_geometries(shp.geometries(), ll, alpha=0.75,
                      edgecolor='#0978ab', facecolor='#f5f4f2', lw=1.0*bwu)

def draw_lithos(ax=None):
    """
    Draw boulder source areas.

    Lithology filters (LEG_GEOL_F):

    * L_ID == 62: Granites, granodiorites, diorites quartiques
    * L_ID == 82: Metagranitoides d'age Paleozoique inferieur (varisque)
    * L_ID == 92: Roches matagabbroiques et eclogitiques
    * L_ID == 98: Glacier, Neve

    Tectonics filters (LEG_TEK_2):

    * T1_ID == 114: Mont-Blanc-Massiv
    * T1_ID == 505: Dent-Blanche-Decke
    * T1_ID == 562: Zone von Zermatt - Saas Fee

    Polygon area filter:

    * AREA == 2276398.0271: Allalin gabbro outcrop on more detailed maps

    """

    # get axes if None provided
    ax = ax or plt.gca()

    # draw swisstopo geology polygons
    filename = '../data/external/swisstopo-geology.shp'
    shp = shpreader.Reader(filename)
    for rec in shp.records():
        atts = rec.attributes
        geom = rec.geometry
        if atts['L_ID'] == 62 and atts['T1_ID'] == 114:
            ax.add_geometries(geom, swiss, alpha=0.75, color='#800000')
        elif atts['L_ID'] == 82 and atts['T1_ID'] == 505:
            ax.add_geometries(geom, swiss, alpha=0.75, color='#000080')
        elif atts['AREA'] == 2276398.0271:
            ax.add_geometries(geom, swiss, alpha=0.75, color='#008000')
            ax.plot(geom.centroid.x, geom.centroid.y, transform=swiss,
                    marker='o', mec='#008000', mew=1.0, mfc='none', ms=12.0)

    # add labels
    txtkwa = dict(fontweight='bold', ha='center', va='center', transform=ll)
    ax.text(6.6, 45.90, 'Mont Blanc granite', color='#800000', **txtkwa)
    ax.text(7.5, 45.75, 'Arolla gneiss', color='#000080', **txtkwa)
    ax.text(8.2, 46.05, 'Allalin gabbro', color='#008000', **txtkwa)

# Natural Earth elements
def draw_rivers(ax=None):
    ax = ax or plt.gca()
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='physical', name='rivers_lake_centerlines', scale=scale,
        edgecolor='#0978ab', facecolor='none', lw=1.0*bwu))

def draw_lakes(ax=None):
    ax = ax or plt.gca()
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='physical', name='lakes', scale=scale,
        edgecolor='#0978ab', facecolor='#c6ecff', lw=0.5*bwu))

def draw_glaciers(ax=None):
    ax = ax or plt.gca()
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='physical', name='glaciated_areas', scale=scale,
        edgecolor='#0978ab', facecolor='#f5f4f2', lw=1.0*bwu, alpha=0.75))

def draw_countries(ax=None):
    ax = ax or plt.gca()
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='cultural', name='admin_0_boundary_lines_land', scale=scale,
        edgecolor='#646464', facecolor='none', lw=1.0*bwu))
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='cultural', name='admin_1_states_provinces_lines', scale=scale,
        edgecolor='#646464', facecolor='none', lw=0.5*bwu))

def draw_graticules(ax=None):
    ax = ax or plt.gca()
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='physical', name='graticules_1', scale=scale,
        edgecolor='#000000', facecolor='none', lw=0.25*bwu))

# Geographic names
def geotag(x, y, text, ax=None, color='k', marker='o', loc='cc',
           offset=5, transform=None, **kwargs):

    # get current axes if None provided
    ax = ax or plt.gca()

    # compute geotransformed coordinates
    if transform is not None:
        x, y = ax.projection.transform_point(x, y, src_crs=transform)

    # compute text offset and alignment
    dx = {'c': 0, 'l': -1, 'r': 1}[loc[1]]*offset
    dy = {'c': 0, 'l': -1, 'u': 1}[loc[0]]*offset
    ha = {'c': 'center', 'l': 'right', 'r': 'left'}[loc[1]]
    va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[loc[0]]
    xytext = kwargs.pop('xytext', (dx, dy))

    # add marker
    ax.plot(x, y, color=color, marker=marker)

    # add annotation
    ax.annotate(text, xy=(x, y), xytext=xytext, textcoords='offset points',
                ha=ha, va=va, **kwargs)

def add_names(ax=None):
    """Add geographic names"""

    # get current axes if None provided
    ax = ax or plt.gca()

    # add names of cities (ll)
    txtkwa = dict(transform=ll, style='italic')
    geotag(6.15, 46.20, 'Geneva', loc='cl', **txtkwa)
    geotag(6.93, 47.00, u'Neuchâtel', loc='lc', **txtkwa)
    geotag(7.45, 46.95, 'Bern', loc='cr', **txtkwa)
    geotag(7.53, 47.22, 'Solothurn', loc='cl', **txtkwa)
    geotag(7.65, 47.23, 'Wangen a.A.', loc='cr', **txtkwa)
    geotag(7.68, 47.17, 'Steinhof', loc='cr', **txtkwa)
    geotag(7.68, 47.14, 'Steineberg', loc='cr', **txtkwa)

    # add names of cities (utm32)
    #txtkwa = dict(transform=proj, style='italic')
    #geotag(280118, 5120218, 'Geneva', **txtkwa)
    #geotag(342883, 5207237, 'Neuchatel', **txtkwa)
    #geotag(382051, 5200774, 'Bern', **txtkwa)
    #geotag(388853, 5229416, 'Solothurn', **txtkwa)
    #geotag(280118, 5120218, 'Geneva', **txtkwa)

    # add boulder sources
    txtkwa = dict(style='italic', offset=15,
                  arrowprops=dict(fc='k', lw=0.5*bwu, arrowstyle='-'))
    geotag(347120, 5103616, 'Mont\nBlanc', xytext=(-20, 0), marker='*', **txtkwa)
    geotag(365930, 5101063, 'Val de\nBagnes', xytext=(0, -20), marker='^', **txtkwa)
    geotag(382491, 5097764, "Val\nd'Arolla", xytext=(0, 20), marker='^', **txtkwa)
    geotag(417299, 5111714, "Saas\nValley", xytext=(-15, 15), marker='^', **txtkwa)

    # add other locations
    txtkwa = dict(color='k', style='italic',
                  ha='center', va='center', transform=ll)
    ax.text(8.10, 46.20, 'Simplon\nPass', rotation=-30, **txtkwa)  # rotation=-45

    # add rivers
    txtkwa = dict(color='#0978ab', style='italic',
                  ha='center', va='center', transform=ll)
    ax.text(7.65, 46.70, 'Aar River', rotation=-45, **txtkwa)
    ax.text(6.30, 46.15, 'Arve River', rotation=-45, **txtkwa)
    ax.text(7.30, 46.25, 'Rhone River', rotation=30, **txtkwa)

    # add mountain massifs
    txtkwa = dict(color='k', fontsize=8, style='italic',
                  ha='center', va='center', transform=ll)
    ax.text(6.2, 46.6, 'JURA\nMOUNTAINS', **txtkwa)
    ax.text(7.7, 46.5, 'AAR MASSIF', **txtkwa)
    ax.text(7.9, 45.9, 'SOUTHERN\nVALAIS', **txtkwa)
    ax.text(6.7, 46.2, 'MONT\nBLANC', **txtkwa)

# modelling domain
def draw_modeldomain(ax=None):
    ax = ax or plt.gca()
    w, e, s, n = 230e3, 470e3, 5050e3, 5240e3
    x = [w, e, e, w, w]
    y = [s, s, n, n, s]
    ax.plot(x, y, c='k', lw=1*bwu, transform=proj)

# modelling domain
def draw_precipzones(ax=None):
    ax = ax or plt.gca()
    for i in range(1, 4):
        x, y = np.loadtxt('../data/native/precip_line_%d.xyz' % i, unpack=True)
        ax.plot(x, y, c='k', lw=1*bwu)

# initialize figure
fig = plt.figure(0, (178/25.4, 120/25.4))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], projection=proj)
ax.set_xlim((w, e))
ax.set_ylim((s, n))
ax.set_rasterization_zorder(2)

# draw stuff
draw_srtm(ax)
draw_rivers(ax)
draw_lakes(ax)
draw_lgm_ehlers(ax)
draw_lithos(ax)
draw_modeldomain(ax)
draw_graticules(ax)
draw_precipzones(ax)
add_names(ax)

# save
fig.savefig('locmap_rhone')
