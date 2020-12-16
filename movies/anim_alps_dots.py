#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Alps scatter plot animations framework."""

import os
import multiprocessing
import numpy as np
import matplotlib.animation as animation
import absplots as apl
import utils as ut


def figure():
    """Prepare initial animation figure."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(192, 108), ncols=2, sharey=True, gridspec_kw=dict(
            left=12, right=4, bottom=8, top=8,
            width_ratios=[3, 1], wspace=4))

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
    ax.set_xlim(10**-10.5, 10**0.5)
    ax.set_ylim(-200, 4700)
    ax.set_xlabel(r'local erosion rate ($m\,a^{-1}$)')
    ax.set_ylabel('modern elevation (m)')

    # plot boot hypsometry
    ax = grid[1]
    bins = np.arange(0, 4501, 100)
    hist, _ = np.histogram(boot.where(boot > 0), bins=bins)
    vals = np.append(hist, hist[-1])  # needed to fill the last bin
    poly = ax.fill_betweenx(bins, 0*vals, vals, color='0.75', step='post')
    hist, _ = np.histogram(boot.where(ds.thk >= 1), bins=bins)
    vals = np.append(hist, hist[-1])  # needed to fill the last bin
    poly = ax.fill_betweenx(bins, 0*vals, vals, color='C1', step='post')
    ax.set_xlim(-2500, 52500)
    ax.set_xticks([])

    # plot dummy erosion rate
    ax = ax.twiny()
    mids = (bins[:-1]+bins[1:])/2
    eroline, = ax.plot(0*mids+1e-9, mids, color='C11')
    # ax.set_xlabel(r'mean erosion rate ($m\,a^{-1}$)', color='C11')
    # ax.set_xscale('log')
    # ax.set_xlim(10**-10.5, 10**0.5)
    ax.set_xlabel(r'band erosion rate ($km^3\,a^{-1}$)', color='C11')
    ax.set_xlim(-0.16*0.05, 0.16*1.05)
    ax.tick_params(axis='x', labelcolor='C11')
    ax.xaxis.set_label_position('bottom')

    # plot mean thickness(thk.plot(ax=ax, y='topg_bins') has issue #3571)
    ax = ax.twiny()
    thk = ds.thk.groupby_bins(boot, bins).mean()
    thkline, = ax.plot(thk, mids, color='C1')
    # ax.set_xlabel('mean ice thickness (m)', color='C1')
    # ax.set_xlim(-50, 1050)
    ax.set_xlabel('band ice volume ($10^3 km^3$)', color='C1')
    ax.set_xlim(-8*0.05, 8*1.05)
    ax.tick_params(axis='x', labelcolor='C1')

    # return figure and animated artists
    return fig, boot, scatter, timetag, poly, eroline, thkline


def animate(time, boot, scatter, timetag, poly, eroline, thkline):
    """Update figure data."""

    # open subdataset
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with ut.open_subdataset(filename, time) as ds:
        icy = ds.thk >= 1.0
        glacthk = ds.thk.where(icy)
        erosion = 2.7e-7 * ds.velbase_mag.where(icy)**2.02

    # replace scatter plot data
    offsets = scatter.get_offsets()
    offsets[:, 0] = erosion.to_masked_array().reshape(-1)
    scatter.set_offsets(offsets)

    # replace text tag
    timetag.set_text('{:,.0f} years ago'.format(-time).replace(',', r'$\,$'))

    # replace histogram data
    path = poly.get_paths()[0]
    nedges = (path.vertices.shape[0]-1)//4  # number of bins + 1
    bins = path.vertices[:2*nedges:2, 1]
    hist, _ = np.histogram(boot.where(icy), bins=bins)
    vals = np.append(hist, hist[-1])  # needed to fill the last bin
    path.vertices[2*nedges:-1, 0] = vals[::-1].repeat(2)

    # for glacier average thickness and geom mean of erosion
    # .set_xdata(glackthk.groupby_bins(boot, bins).mean())
    # .set_xdata(np.exp(np.log(erosion).groupby_bins(boot, bins).mean()))

    # glacier volume (1e3*km3) and volumic erosion (km3 a-1) over band
    thkline.set_xdata(glacthk.groupby_bins(boot, bins).sum()/1e6)
    eroline.set_xdata(erosion.groupby_bins(boot, bins).sum()/1e3)

    # return animated artists
    return scatter, timetag, poly, eroline, thkline


def update(time, *fargs):
    """Update artists to given animation time and return."""
    animate(time, *fargs)
    return fargs[-1].figure


def parallelframes(fig, *fargs, frames=range(-119960, 1, 40)):
    """Save all frames individually in parallel (est. 2.5 h on altair)."""

    # create output frames directory if missing
    outdir = os.path.join(os.environ['HOME'], 'anim', 'anim_alps_dots')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # iterable arguments to save animation frames
    iargs = [(update, outdir, time, *fargs) for time in frames]

    # plot all frames in parallel
    with multiprocessing.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, iargs)


def serialanimation(fig, *fargs, frames=range(-119960, 1, 40)):
    """Direct matplotlib serial animation (est. 4.5 h on altair)."""
    ani = animation.FuncAnimation(
        fig, animate, blit=True, interval=1000/25, fargs=fargs, frames=frames)
    ani.save('anim_alps_dots.mp4')


def simplefigure(fig, time, *fargs):
    """Plot one frame and save as figure."""
    animate(time, *fargs)
    fig.savefig('anim_alps_dots')


def main():
    """Main program called during execution."""
    fig, *fargs = figure()
    parallelframes(fig, *fargs, frames=range(-120000+40, 1, 40))
    simplefigure(fig, -25000, *fargs)


if __name__ == '__main__':
    main()
