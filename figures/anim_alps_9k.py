#!/usr/bin/env python

import os
import sys
import multiprocessing as mp
import matplotlib.pyplot as plt
import util

# frames output directory
videoname = os.path.basename(os.path.splitext(sys.argv[0])[0])
framesdir = os.path.join(os.environ['HOME'], 'anim', videoname)

# start and end of animation
t0, t1, dt = -120000, 0, 1000


def draw(t):
    """Plot complete figure for given time."""

    # check if file exists
    fname = os.path.join(framesdir, '{:06d}.png'.format(t+120000))
    if not os.path.isfile(fname):

        # initialize figure
        print('plotting {:s} ...'.format(fname))
        fig, ax = util.fig.subplots_anim(extent='alps', figsize=(900.0, 600.0))

        # prepare axes coordinates
        x, y = util.pl.coords_from_extent(ax.get_extent(),
                                        *fig.get_size_inches()*fig.dpi)

        # estimate sea level drop
        dsl = util.io.open_sealevel(t)

        # plot interpolated data
        filename = '~/pism/' + util.alpcyc_bestrun + 'y{:07.0f}-extra.nc'
        with util.io.open_visual(filename, t, x, y) as ds:
            util.xp.ice_extent(ds.icy, ax=ax, fc='w')
            util.xp.topo_contours(ds.usurf, ax=ax)

        # plot extra data
        with util.io.open_subdataset(filename, t) as ds:
            util.xp.streamplot(ds, ax=ax, density=(60, 40))

        # save
        fig.savefig(fname, facecolor='none')
        plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frames directory if missing
    if not os.path.isdir(framesdir):
        os.mkdir(framesdir)

    # plot all frames in parallel
    pool = mp.Pool(processes=4)
    pool.map(draw, range(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
