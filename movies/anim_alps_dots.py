#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Alps scatter plot animations framework."""

import numpy as np
import matplotlib.animation as animation
import absplots as apl
import utils as ut

# FIXME add probability densities, maybe a timeline


def figure():
    """Prepare initial animation figure."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(192, 108), ncols=2, sharey=True, gridspec_kw=dict(
            left=12, right=4, bottom=8, top=8, width_ratios=[3, 1]))

    # load boot topo
    with ut.open_dataset('../data/processed/alpcyc.1km.in.nc') as ds:
        boot = ds.topg

    # plot dummy scatter and age tag
    ax = grid[0]
    scatter = ax.scatter(0*boot, boot, alpha=0.05, color='C11', marker='.')
    timetag = ax.text(0.95, 0.95, '', ha='right', va='top',
                      transform=ax.transAxes)

    # set axes properties
    ax.set_xscale('log')
    ax.set_xlim(1e-9/9, 9*1e0)
    ax.set_ylim(-200, 4700)
    ax.set_xticks(np.logspace(-9, 0, 10))
    ax.set_xlabel(r'erosion rate ($m\,a^{-1}$)')
    ax.set_ylabel('elevation (m)')

    # plot boot hypsometry
    ax = grid[1]
    bins = range(0, 4501, 100)
    ax.hist(boot.where(boot > 0).values.reshape(-1), bins=bins,
            color='0.75', orientation='horizontal')
    ax.set_xticks([])

    # return figure and animated artists
    return fig, scatter, timetag


def animate(time, scatter, timetag):
    """Update figure data."""

    # open subdataset
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with ut.open_subdataset(filename, time) as ds:
        erosion = (2.7e-7*ds.velbase_mag**2.02).where(ds.thk >= 1.0)

    # replace scatter plot data
    offsets = scatter.get_offsets()
    offsets[:, 0] = erosion.to_masked_array().reshape(-1)
    scatter.set_offsets(offsets)

    # replace text tag
    timetag.set_text('{:,.0f} years ago'.format(-time).replace(',', r'$\,$'))

    # return animated artists
    return scatter, timetag


def main():
    """Main program called during execution."""

    # prepare figure
    fig, *fargs = figure()
    animate(-25000, *fargs)
    fig.savefig('anim_alps_dots')

    # animation
    # FIXME can't use blit with histogram
    ani = animation.FuncAnimation(
        fig, animate, blit=True, interval=1000/25, fargs=(scatter, timetag),
        frames=range(-119000, 1, 400))
    ani.save('anim_alps_dots.mp4')


if __name__ == '__main__':
    main()
