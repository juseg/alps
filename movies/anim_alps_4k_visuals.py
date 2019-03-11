#!/usr/bin/env python
# coding: utf-8

import os
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import utils as ut


def visual(t, crop='al', mode='co', t0=-120000, t1=-0):
    """Plot main figure for given time."""

    # initialize figure
    fig, ax = ut.axes_anim_dynamic(crop, t, t0=t0, t1=t1, figsize=(384, 216))
    x, y = ut.coords_from_axes(ax)

    # estimate sea level drop
    dsl = ut.open_sealevel(t)

    # plot interpolated data
    filename = ('~/pism/output/e9d2d1f/alps-wcnn-1km/'
                'epica3222cool1220+alpcyc4+pp/y{:07.0f}-extra.nc')
    with ut.open_visual(filename, t, x, y) as ds:
        ut.plot_shaded_relief(ds.topg-dsl, ax=ax, mode=mode)
        ut.plot_topo_contours(ds.usurf, ax=ax)
        ut.plot_ice_extent(ds.icy, ax=ax, fc=('w' if mode == 'co' else 'none'))

        # in greyscale mode, show interpolated velocities
        if mode == 'gs':
            ds.velsurf_mag.plot.imshow(
                ax=ax, add_colorbar=False, alpha=0.75,
                cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3))

    # in color mode, stream plot extra data
    if mode == 'co':
        with ut.open_subdataset(filename, t) as ds:
            ut.plot_streamlines(ds, ax=ax, density=(24, 16))

    # draw map elements
    ut.draw_tailored_hydrology(ax=ax, mode=mode)
    ut.draw_lgm_faded(ax=ax, t=t)

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'zo'])
    parser.add_argument('mode', choices=['co', 'gs'])
    args = parser.parse_args()

    # start and end of animation
    if args.crop in ('lu', 'ma'):
        t0, t1, dt = -45000, -15000, 10
    else:
        t0, t1, dt = -120000, -0, 40

    # output frame directories
    prefix = os.path.join(os.environ['HOME'], 'anim', 'anim_alps_4k')
    outdir = prefix + '_main_' + args.crop + '_' + args.mode

    # iterable arguments to save animation frames
    iter_args = [(visual, outdir, t, args.crop, args.mode, t0, t1)
                 for t in range(t0+dt, t1+1, dt)]

    # create frame directory if missing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
