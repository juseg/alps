#!/usr/bin/env python
# coding: utf-8

import os
import sys
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import util as ut

# crop region and language
crop = 'zo'  # al ch lu zo
lang = 'en'  # de en fr it ja nl
mode = 'co'  # co gs

# japanese input
if lang == 'ja':
    plt.rc('font', family='TakaoPGothic')

# prefix for output files
prefix = os.path.basename(os.path.splitext(sys.argv[0])[0])
prefix = os.path.join(os.environ['HOME'], 'anim', prefix)

# start and end of animation
# FIXME this depends on crop region, suffix = '_%d%d' % (-t0/1e3, t1/1e3)
t0, t1, dt = -120000, -0, 40


def plot_main(t):
    """Plot main figure for given time."""

    # check if file exists
    fname = '{}_main_{}_{}/{:06d}.png'.format(prefix, crop, mode, t+120000)
    if not os.path.isfile(fname):

        # initialize figure
        print('plotting {:s} ...'.format(fname))
        fig, ax = ut.subplots_anim_dynamic(crop, t=t, t0=t0, t1=t1,
                                           figsize=(384.0, 216.0))

        # prepare axes coordinates
        x, y = ut.coords_from_extent(ax.get_extent(),
                                     *fig.get_size_inches()*fig.dpi)

        # estimate sea level drop
        dsl = ut.open_sealevel(t)

        # plot interpolated data
        filename = ('~/pism/output/e9d2d1f/alps-wcnn-1km/'
                    'epica3222cool1220+alpcyc4+pp/y{:07.0f}-extra.nc')
        with ut.open_visual(filename, t, x, y) as ds:
            ut.plot_shaded_relief(ds.topg-dsl, ax=ax, mode=mode)

            # in greyscale mode, show interpolated velocities
            if mode == 'gs':
                ds.velsurf_mag.plot.imshow(
                    ax=ax, add_colorbar=False, alpha=0.75,
                    cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3))

            # add surface topo and ice extent
            ut.plot_topo_contours(ds.usurf, ax=ax)
            ut.plot_ice_extent(ds.icy, ax=ax, fc=dict(co='w', gs='none')[mode])

        # in color mode, stream plot extra data
        if mode == 'co':
            with ut.open_subdataset(filename, t) as ds:
                ut.plot_streamlines(ds, ax=ax, density=(24, 16))

        # draw map elements
        ut.draw_tailored_hydrology(ax=ax, mode=mode)

        # draw lgm with fade-in and fade-out
        tred = (t+25000) / 5000
        fade = tred**4 - 2*tred**2 + 1
        if mode == 'gs' and abs(tred) < 1:
            ut.draw_lgm_outline(ax=ax, alpha=0.75*fade)

        # save
        fig.savefig(fname, dpi=254.0)
        plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frame directories if missing
    for suffix in ['_main_'+crop+'_'+mode]:
        if not os.path.isdir(prefix + suffix):
            os.mkdir(prefix + suffix)

    # plot all frames in parallel
    pool = mp.Pool(processes=4)
    pool.map(plot_main, range(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
