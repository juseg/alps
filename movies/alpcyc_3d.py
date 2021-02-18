#!/usr/bin/env python
# Copyright (c) 2016-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alpine ice sheet 3D animation."""

import os.path
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp

import cartowik.conventions as ccv
import pismx.open

from alpcyc_4k import save_animation_frame


def add_cities(ax=None, lang=None, include=None, exclude=None, ranks=None,
               **kwargs):
    """Plot populated places as an annotated scatter plot. This is a variation
    of cartowik.naturalearth.add_cities for 3D axes."""

    # get current axes if None provided
    ax = ax or plt.gca()

    # open shapefile data
    shp = cshp.Reader(cshp.natural_earth(
        resolution='10m', category='cultural', name='populated_places'))

    # filter by rank, include and exclude
    records = shp.records()
    if ranks is not None:
        records = [rec for rec in records if (
            rec.attributes['SCALERANK'] in ranks and
            rec.attributes['name_en'] not in (exclude or []) or
            rec.attributes['name_en'] in (include or []))]

    # convert coordinates (add 100m so points stay above surface)
    points = np.array(
        [[rec.geometry.x, rec.geometry.y, rec.attributes['GTOPO30']+100]
         for rec in records])
    points = ccrs.UTM(32).transform_points(ccrs.PlateCarree(), *points.T)

    # add text labels
    if lang is not None:
        for point, rec in zip(points, records):
            if np.inf not in point:
                ax.text(
                    *point, rec.attributes['name_'+lang]+'\n',
                    color=kwargs.get('color'), ha='center')

    # return scatter plot
    return ax.scatter(*points.T, **kwargs)


def pan_out(ax, years, start=-120e3, end=-0e3):
    """Dynamic axes extent and camera location."""

    # smoothly increasing zoomout factor
    zoom = (years-start)/(end-start)  # linear increase between 0 and 1
    zoom = zoom**2*(3-2*zoom)  # smooth zoom factor between 0 and 1

    # set camera location
    ax.view_init(azim=75+90*zoom, elev=15+15*zoom)

    # set axes limits (note: the centre of rotation is near the upper edge of
    # the figure because the axes are square and extending outside of the
    # figure. Using a positive zmid will move the data towards the centre of
    # the figure.)
    xmid, ymid, zmid = 600e3, 5120e3, 3e3  # domain centre
    half = 25e3 + 100e3*zoom  # evolving domain half-width
    ax.set_xlim(xmid-half, xmid+half)
    ax.set_ylim(ymid-half, ymid+half)
    ax.set_zlim(zmid-half/5, zmid+half/5)  # vertical exageration


def figure(years):
    """Plot one animation frame, return figure."""

    # initialize figure (this is a total enigma to me, but apparently the axes
    # rect need to be squared and aligned with the figure bottom so that the
    # drawing fills the entire figure, and then the zlim needs to be adjusted
    # so that it comes back down into view)
    fig = plt.figure(0, (192/25.4, 108/25.4))
    ax = fig.add_axes([0, 0, 1, 16/9], projection='3d')

    # estimate sea level drop
    dsl = pd.read_csv(
        '../data/external/spratt2016.txt', comment='#', delimiter='\t',
        index_col='age_calkaBP').to_xarray()
    dsl = dsl.SeaLev_shortPC1.dropna('age_calkaBP')
    dsl = min(dsl.interp(age_calkaBP=-years/1e3, method='cubic').values, 0.0)

    # load extra data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with pismx.open.subdataset(filename, years, shift=120000) as ds:

        # prepare composite image of topo and velocity
        img = np.where(
            (ds.thk > 1.0).expand_dims('color', axis=-1),  # add dimension
            plt.get_cmap('Blues')(mcolors.LogNorm(1e1, 1e3)(ds.velsurf_mag)),
            ccv.TOPOGRAPHIC(mcolors.Normalize(0e3, 4.5e3)(ds.topg-dsl)))

        # put blue color below interpolated sea level
        # this does not work because usurf contains no bathymetry
        img[ds.topg < dsl] = (0.776, 0.925, 1, 0)  # c6ecff

        # plot surface elevation and drape with image
        ax.plot_surface(
            *np.meshgrid(ds.x, ds.y), ds.usurf, facecolors=img,
            rstride=1, cstride=1, linewidth=0)

    # draw map elements
    add_cities(
        ax=ax, lang='en', color='0.25', marker='o',
        exclude=['Monaco'], ranks=range(7))

    # set pan-out effect
    pan_out(ax, years)
    ax.set_axis_off()

    # add age tag
    fig.text(
        0.95, 0.95, '{:,.0f} years ago'.format(-years).replace(',', r'$\,$'),
        ha='right', va='top', fontweight='bold')

    # return figure
    return fig


def main():
    """Main program called during execution."""

    # iterable arguments to save animation frames
    outdir = os.path.expanduser('~/anim/' + os.path.basename(__file__[:-3]))
    iargs = [(figure, outdir, years) for years in range(-120000+4000, 1, 4000)]

    # plot all frames in parallel
    with multiprocessing.Pool(processes=4) as pool:
        pool.starmap(save_animation_frame, iargs)


if __name__ == '__main__':
    main()
