#!/usr/bin/env python
# coding: utf-8

import os
import sys
import multiprocessing as mp
import matplotlib.pyplot as plt
import xarray as xr
import util as ut

# frames output directory
videoname = os.path.basename(os.path.splitext(sys.argv[0])[0])
framesdir = os.path.join(os.environ['HOME'], 'anim', videoname)

# start and end of animation
t0, t1, dt = -120000, 0, 5000


def draw(t):
    """Plot complete figure for given time."""

    # check if file exists
    framepath = os.path.join(framesdir, '{:06d}.png'.format(t+120000))
    if not os.path.isfile(framepath):

        # initialize figure
        print 'plotting {:s} ...'.format(framepath)
        fig, ax = ut.fi.subplots_anim(extent='alps', figsize=(900.0, 600.0))

        # prepare axes coordinates
        x, y = ut.pl.coords_from_extent(ax.get_extent(),
                                        *fig.get_size_inches()*fig.dpi)

        # estimate sea level drop
        # FIXME preprocess or fix mfoutput ages, then remove xarray import
        with xr.open_dataset(os.environ['HOME']+'/pism/input/dsl/specmap.nc',
                             decode_times=False) as ds:
            dsl = ds.delta_SL.interp(time=t).data

        # load interpolated data
        filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
        with ut.io.load_visual(filepath, t, x, y) as ds:

            # plot surface topography
            ds.icy.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors='w',
                                 extend='neither', levels=[0.5, 1.5])
            ds.icy.plot.contour(ax=ax, colors=['0.25'], levels=[0.5],
                                linewidths=0.25)
            ds.usurf.plot.contour(ax=ax, colors=['0.25'], levels=ut.pl.inlevs,
                                  linewidths=0.1)
            ds.usurf.plot.contour(ax=ax, colors=['0.25'], levels=ut.pl.utlevs,
                                  linewidths=0.25)

        # load extra data
        with ut.io.load_mfoutput(filepath) as ds:

            # extract velocities
            ds = ds.sel(age=-t)
            x = ds.x
            y = ds.y
            u = ds.uvelsurf.where(ds.thk.fillna(0.0) >= 1.0).values
            v = ds.vvelsurf.where(ds.thk.fillna(0.0) >= 1.0).values
            c = (u**2+v**2)**0.5

            # try add streamplot (start point spacing 0.5 km == 5 px)
            try:
                ax.streamplot(x, y, u, v, cmap='Blues', color=c,
                              density=(60.0, 40.0), norm=ut.pl.velnorm,
                              linewidth=0.5, arrowsize=0.25)

            # handle lack of ice cover
            except ValueError:
                pass

        # save
        fig.savefig(framepath, facecolor='none')
        plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # create frames directory if missing
    if not os.path.isdir(framesdir):
        os.mkdir(framesdir)

    # plot all frames in parallel
    pool = mp.Pool(processes=4)
    pool.map(draw, xrange(t0+dt, t1+1, dt))
    pool.close()
    pool.join()
