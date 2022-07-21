#!/usr/bin/env python
# Copyright (c) 2016-2022, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps boulders location map."""


import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartowik.annotations as can
import cartowik.shadedrelief as csr
import util


def draw_shaded_relief(ax=None):
    """Draw high-resolution shaded relief background"""

    # get axes if None provided
    ax = ax or plt.gca()

    # plot SRTM bedrock topography FIXME use hyoga methods
    with xr.open_dataset(
            '~/pism/input/boot/alps.srtm.hus12.100m.nc') as ds:
        srtm = ds.usurf.fillna(0.0) - ds.thk.fillna(0.0)
        csr._add_imshow(srtm, ax=ax, cmap='Topographic', vmin=0, vmax=4500)
        srtm = csr._compute_multishade(srtm)
        csr._add_imshow(srtm, ax=ax, cmap='Shines', vmin=-1.0, vmax=1.0)


def draw_lithologies(ax=None):
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

    # prepare colors
    granite = 'C5'
    gneiss = 'C1'
    gabbro = 'C3'

    # draw swisstopo polygons
    swiss = ccrs.TransverseMercator(
        central_longitude=7.439583333333333,
        central_latitude=46.95240555555556,
        false_easting=600e3, false_northing=200e3, approx=False)
    shp = shpreader.Reader('../data/external/PY_Surface_Base.shp')
    for rec in shp.records():
        atts = rec.attributes
        geom = rec.geometry
        if atts['L_ID'] == 62 and atts['T1_ID'] == 114:
            ax.add_geometries([geom], swiss, alpha=0.75, color=granite)
        elif atts['L_ID'] == 82 and atts['T1_ID'] == 505:
            ax.add_geometries([geom], swiss, alpha=0.75, color=gneiss)
        elif atts['AREA'] == 2276398.0271:
            ax.add_geometries([geom], swiss, alpha=0.75, color=gabbro)
            ax.plot(geom.centroid.x, geom.centroid.y, transform=swiss,
                    marker='o', mec=gabbro, mew=1.0, mfc='none', ms=12.0)

    # add labels
    txtkwa = dict(fontweight='bold', ha='center', va='center',
                  transform=ccrs.PlateCarree())
    ax.text(6.7, 45.90, 'Mont Blanc\ngranite', color=granite, **txtkwa)
    ax.text(7.5, 45.75, 'Arolla gneiss', color=gneiss, **txtkwa)
    ax.text(8.1, 46.10, 'Allalin\ngabbro', color=gabbro, **txtkwa)


# FIXME more flexibility in cartowik annotations or annotated scatter
def geotag(x, y, text, ax=None, color='k', marker='o', transform=None,
           **kwargs):
    """Add geographic marker and annotation."""
    ax = ax or plt.gca()

    # compute geotransformed coordinates
    if transform is not None:
        coords = ax.projection.transform_point(x, y, src_crs=transform)

    # add marker
    ax.plot(*coords, color=color, marker=marker)
    can.annotate_by_compass(text, ax=ax, xy=coords, **kwargs)


def add_names(ax=None):
    """Add geographic names"""

    # get current axes if None provided
    ax = ax or plt.gca()

    # add names of cities
    lonlat = ccrs.PlateCarree()
    txtkwa = dict(ax=ax, transform=lonlat, marker='o', style='italic')
    # geotag(6.15, 46.20, 'Geneva', point='w', **txtkwa)
    geotag(6.93, 47.00, u'Neuchâtel', point='s', **txtkwa)
    geotag(7.45, 46.95, 'Bern', point='e', **txtkwa)
    geotag(7.53, 47.22, 'Solothurn', point='w', **txtkwa)
    geotag(7.65, 47.23, 'Wangen a.A.', point='e', **txtkwa)
    geotag(7.68, 47.16, 'Steinhof', point='e', **txtkwa)

    # add names of mountains
    txtkwa = dict(ax=ax, transform=lonlat, marker='+', style='italic')
    geotag(7.68, 47.14, 'Steinenberg', point='s', **txtkwa)
    geotag(6.90, 45.80, 'Mont Blanc', point='w', **txtkwa)

    # add boulder sources
    ax.plot(347120, 5103616, color='C4', marker='*', ms=8)  # Mt Blanc
    ax.plot(365930, 5101063, color='C1', marker='^', ms=8)  # Val de Bagnes
    ax.plot(382491, 5097764, color='C1', marker='^', ms=8)  # Val d'Arolla
    ax.plot(417299, 5111714, color='C2', marker='s', ms=8)  # Saastal

    # add other locations
    txtkwa = dict(color='k', style='italic',
                  ha='center', va='center', transform=lonlat)
    ax.text(6.00, 46.17, 'Geneva\nBasin', **txtkwa)
    ax.text(7.25, 46.00, 'Val de Bagnes', rotation=-40, **txtkwa)
    ax.text(7.45, 46.15, "Val d'Arolla", rotation=-60, **txtkwa)
    ax.text(7.97, 46.07, 'Saastal', rotation=-60, **txtkwa)
    ax.text(8.10, 46.20, 'Simplon Pass', rotation=-30, **txtkwa)

    # add palaeo-glaciers
    txtkwa = dict(color='#0978ab', style='italic', fontweight='bold',
                  fontsize=8, ha='center', va='center', transform=lonlat)
    ax.text(5.30, 45.75, 'Lyon Lobe', rotation=0, **txtkwa)
    ax.text(6.50, 46.05, 'Arve Glacier', rotation=-5, **txtkwa)
    ax.text(7.60, 46.80, 'Aar Glacier', rotation=-55, **txtkwa)
    ax.text(7.35, 46.95, 'Solothurn Lobe', rotation=40, **txtkwa)
    ax.text(7.00, 46.35, 'Valais Glacier', rotation=-65, **txtkwa)

    # add mountain massifs
    txtkwa = dict(color='k', fontsize=8, style='italic',
                  ha='center', va='center', transform=lonlat)
    ax.text(6.2, 46.6, 'JURA\nMOUNTAINS', **txtkwa)
    ax.text(7.7, 46.5, 'AAR MASSIF', **txtkwa)
    ax.text(7.9, 45.9, 'SOUTHERN\nVALAIS', **txtkwa)
    ax.text(6.7, 46.2, 'MONT\nBLANC', **txtkwa)


def draw_rhone_arrows(ax=None):
    """Draw symbolic glacier flow arrows."""
    ax = ax or plt.gca()
    arrowprops = dict(
        arrowstyle='-|>',
        mutation_scale=20.0, transform=ccrs.PlateCarree(),
        color='#0978ab', lw=2.0, zorder=2)
    ax.add_patch(mpatches.FancyArrowPatch(
        (7.05, 46.15), (6.05, 46.20),
        connectionstyle='arc,angleA=115,angleB=45,armA=350,armB=0,rad=100.0',
        **arrowprops))
    ax.add_patch(mpatches.FancyArrowPatch(
        (7.05, 46.15), (7.60, 47.20),
        connectionstyle='arc,angleA=115,angleB=-135,armA=350,armB=0,rad=100.0',
        **arrowprops))


def draw_precip_zones(ax=None):
    """Draw Guillaume's precipitation zones."""
    ax = ax or plt.gca()
    for i in range(1, 4):
        x, y = np.loadtxt('../data/native/precip_line_%d.xyz' % i, unpack=True)
        ax.plot(x, y, c='k', lw=0.5)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax, cax = util.fig.subplots_cax(extent='boulders')
    cax.set_visible(False)  # FIXME add util.fig.subplots without cax

    # draw stuff
    # FIXME wait for cartopy issue #1282 or implement cartowik fiona compat
    draw_shaded_relief(ax=ax)
    # draw_lithologies(ax=ax)
    draw_precip_zones(ax=ax)
    draw_rhone_arrows(ax=ax)
    add_names(ax=ax)
    util.geo.draw_model_domain(ax=ax, extent='guil')
    util.geo.draw_lgm_outline(ax=ax, edgecolor='#0978ab', facecolor='w')
    util.geo.draw_natural_earth(ax=ax, mode='co')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
