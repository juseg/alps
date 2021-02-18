#!/usr/bin/env python
# Copyright (c) 2016-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import os.path
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import cartowik.conventions as ccv
import pismx.open

from alpcyc_4k import save_animation_frame


def figure(years):
    """Plot one animation frame, return figure."""

    # initialize figure (this is a total enigma to me, but apparently the axes
    # rect need to be squared and aligned with the figure bottom so that the
    # drawing fills the entire figure, and then the zlim needs to be adjusted
    # so that it comes back down into view)
    fig = plt.figure(0, (192/25.4, 108/25.4))
    ax = fig.add_axes([0, 0, 1, 16/9], projection='3d')
    ax.view_init(azim=165, elev=30)

    # estimate sea level drop
    dsl = pd.read_csv(
        '../data/external/spratt2016.txt', comment='#', delimiter='\t',
        index_col='age_calkaBP').to_xarray().SeaLev_shortPC1.dropna('age_calkaBP')
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
        img[ds.topg < dsl] = (0.776, 0.925, 1, 0)  #c6ecff

        # plot surface elevation and drape with image
        xx, yy = np.meshgrid(ds.x, ds.y)
        ax.plot_surface(
            xx, yy, ds.usurf, vmin=0.0, vmax=3e3, facecolors=img,
            rstride=1, cstride=1, linewidth=0, alpha=1.0)

    # set axes limits 250x250 km
    ax.set_xlim(475e3, 725e3)    # default  (105e3, 1095e3) mid 600
    ax.set_ylim(4995e3, 5245e3)  # default (4790e3, 5450e3) mid 5120
    ax.set_zlim(-12e3, 12e3)     # default (-100, 4500)
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
