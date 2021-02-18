#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Alpine glacial cycle erosion vs altitude."""

import os
import multiprocessing
import numpy as np
import absplots as apl
import pismx.open

from alpcyc_4k import save_animation_frame


def figure(years):
    """Plot one animation frame, return figure."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(192, 108), ncols=2, sharey=True, gridspec_kw=dict(
            left=15, right=5, bottom=10, top=10,
            width_ratios=[3, 1], wspace=5))

    # load boot topo
    with pismx.open.dataset('../data/processed/alpcyc.1km.in.nc') as ds:
        boot = ds.topg

    # open extra output
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with pismx.open.subdataset(filename, years, shift=120000) as ds:
        erosion = (5.2e-8*ds.velbase_mag**2.34).where(ds.thk >= 1)  # mm a-1

        # add erosion scatter plot
        ax = grid[0]
        ax.scatter(erosion, boot.where(ds.thk >= 1),
                   alpha=0.25, color='C11', edgecolor='none', marker='.', s=1)

        # set axes properties
        ax.set_xscale('log')
        ax.set_xlim(10**-10.5, 10**0.5)
        ax.set_xticks([10**i for i in range(-10, 1, 2)])
        ax.set_ylim(-200, 4700)
        ax.set_xlabel(r'local erosion rate ($mm\,a^{-1}$)')
        ax.set_ylabel('current bedrock elevation (m)')

        # add age tag
        ax.text(
            0.95, 0.95,
            '{:,.0f} years ago'.format(-years).replace(',', r'$\,$'),
            ha='right', va='top', fontweight='bold', transform=ax.transAxes)

        # plot boot and glacierized hypsometry
        # NOTE: color cycle is affected in 4k anim. Homogenize
        ax = grid[1]
        bins = np.arange(0, 4501, 100)
        ax.hist(boot.where(boot > 0).values.ravel(), bins=bins,
                orientation='horizontal', color='0.75')
        ax.hist(boot.where(ds.thk >= 1).values.ravel(), bins=bins,
                orientation='horizontal', color='C1')

        # set axes properties
        ax.set_xlim(-2500, 52500)
        ax.set_xticks([])

        # plot band erosion rate
        ax = ax.twiny()
        (np.exp(np.log(erosion).groupby_bins(boot, bins).mean())).plot(
            ax=ax, y='topg_bins', color='C11')

        # set axes properties
        ax.set_xlabel(r'geom. mean erosion rate ($mm\,a^{-1}$)', color='C11')
        ax.set_xscale('log')
        ax.set_xlim(10**-10.5, 10**0.5)
        ax.set_xticks([10**i for i in range(-10, 1, 2)])
        ax.tick_params(axis='x', labelcolor='C11')
        ax.xaxis.set_label_position('bottom')
        ax.set_title('')

        # plot band ice thickness
        ax = ax.twiny()
        (ds.thk.where(ds.thk >= 1).groupby_bins(boot, bins).mean()).plot(
            ax=ax, y='topg_bins', color='C1')

        # set axes properties
        ax.set_xlabel('mean ice thickness (m)', color='C1')
        ax.set_xlim(-50, 1050)
        ax.tick_params(axis='x', labelcolor='C1')
        ax.set_title('')

    # return figure
    return fig


def main():
    """Main program called during execution."""

    # iterable arguments to save animation frames
    outdir = os.path.expanduser('~/anim/' + os.path.basename(__file__[:-3]))
    iargs = [(figure, outdir, years) for years in range(-120000+40, 1, 40)]

    # plot all frames in parallel
    with multiprocessing.Pool(processes=4) as pool:
        pool.starmap(save_animation_frame, iargs)


if __name__ == '__main__':
    main()
