#!/usr/bin/env python
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps 4k animations frames main visuals."""

import os
import argparse
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pismx.open
import utils as ut


def visual(time, crop='al', mode='co', start=-120000, end=-0):
    """Plot main figure for given time."""

    # initialize figure
    fig, ax = ut.axes_anim_dynamic(
        crop, time, start=start, end=end, figsize=(384, 216))

    # estimate sea level drop
    dsl = ut.open_sealevel(time)

    # plot interpolated data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    with pismx.open.visual(
            filename, '../data/processed/alpcyc.1km.in.nc',
            '../data/external/srtm.nc', ax=ax, time=time, shift=120000) as ds:
        if mode != 'ga':
            ut.plot_shaded_relief(ds.topg-dsl, ax=ax, mode=mode)
            ut.plot_ice_extent(
                ds.icy, ax=ax, fc=('w' if mode in 'co' else 'none'))
        ut.plot_topo_contours(ds.usurf, ax=ax)

    # mode co, stream plot extra data
    if mode == 'co':
        with pismx.open.subdataset(filename, time=time, shift=120000) as ds:
            ut.plot_streamlines(ds, ax=ax, density=(24, 16))

    # mode er, interpolate erosion rate
    # (values range 1e-16 to 1e2, mostly within 1e-12 to 1e-2)
    elif mode == 'er':
        (5.2e-8*ds.velbase_mag**2.34).where(ds.icy).plot.contourf(
            ax=ax, add_colorbar=False, alpha=0.75, cmap='YlOrBr',
            levels=[10**i for i in range(-9, 1)])

    # mode ga or gs, show interpolated velocities
    elif mode in ('ga', 'gs'):
        ds.velsurf_mag.plot.imshow(
            ax=ax, add_colorbar=False, alpha=0.75,
            cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3))

    # mode ul, show interpolated bedrock depression
    elif mode == 'ul':
        ds.uplift.plot.contourf(
            ax=ax, add_colorbar=False, alpha=0.75, cmap='PRGn_r',
            levels=[-100, -50, -20, 0, 2, 5, 10])

        # locate maximum depression (xarray has no idxmin yet)
        i, j = divmod(int(ds.uplift.argmin()), ds.uplift.shape[1])
        maxdep = float(-ds.uplift[i, j])
        color = 'w' if maxdep > 50 else 'k'
        ax.plot(ds.x[j], ds.y[i], 'o', color=color, alpha=0.75)
        ax.text(ds.x[j]+5e3, ds.y[i]+5e3, '{:.0f} m'.format(maxdep),
                color=color)

    # draw map elements
    if mode != 'ga':
        ut.draw_tailored_hydrology(ax=ax, mode=mode)
    if mode == 'gs':
        ut.draw_lgm_faded(ax=ax, t=time)

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'ul', 'zo'])
    parser.add_argument('mode', choices=['co', 'er', 'ga', 'gs', 'ul'])
    args = parser.parse_args()

    # set default font size for uplift tag and colorbars
    plt.rc('font', size=12)

    # start and end of animation
    if args.crop in ('lu', 'ma'):
        start, end, step = -45000, -15000, 10000
    else:
        start, end, step = -120000, -0, 4000

    # output frame directories
    prefix = os.path.join(os.environ['HOME'], 'anim', 'anim_alps_4k')
    outdir = prefix + '_main_' + args.crop + '_' + args.mode

    # iterable arguments to save animation frames
    iter_args = [(visual, outdir, t, args.crop, args.mode, start, end)
                 for t in range(start+step, end+1, step)]

    # create frame directory if missing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=8) as pool:
        pool.starmap(ut.save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
