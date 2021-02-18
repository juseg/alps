#!/usr/bin/env python
# Copyright (c) 2016-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import os.path
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import cartowik.conventions as ccv
import pismx.open

from alpcyc_4k import save_animation_frame

# meshing stride
stride = 1

def figure(years):
    """Plot one animation frame, return figure."""

    # load extra data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    nc= pismx.open.subdataset(filename, years, shift=120000)

    # select time slice data
    # FIXME use sel coords instead of isel indices
    w, e, s, n = 250, 400, 355, 455  # Zürich
    w, e, s, n = 125, 425, 300, 500  # Swiss foreland
    w, e, s, n = 000, 901, 000, 601  # Whole domain
    nc = nc.isel(x=slice(w, e, stride), y=slice(s, n, stride))
    x = nc.x
    y = nc.y
    xx, yy = np.meshgrid(x, y)
    thk = nc.thk  #[w:e:stride, s:n:stride].T
    usurf = nc.usurf  #[w:e:stride, s:n:stride].T
    velsurf = nc.velsurf_mag  #[w:e:stride, s:n:stride].T
    age = nc.age.squeeze()

    # initialize figure (this is a total enigma to me, but apparently the axes
    # rect need to be squared and aligned with the figure bottom so that the
    # drawing fills the entire figure, and then the zlim needs to be adjusted
    # so that it comes back down into view)
    fig = plt.figure(0, (192/25.4, 108/25.4))
    ax = fig.add_axes([0, 0, 1, 16/9], projection='3d')
    ax.view_init(azim=165, elev=30)
    label = fig.text(0.05, 0.90, '', bbox=dict(ec='k', fc='w'))

    # prepare composite image of topo and velocity
    topocmap = ccv.TOPOGRAPHIC  #plt.get_cmap('Greys')
    toponorm = mcolors.Normalize(0e3, 4.5e3)  #mcolors.Normalize(0e3, 3e3)
    topo_img = topocmap(toponorm(usurf))
    velocmap = plt.get_cmap('Blues')
    velonorm = mcolors.LogNorm(1e1, 1e3)
    velo_img = velocmap(velonorm(velsurf))
    mask = (thk > 1.0).data[:, :, None]  # add one dimension
    mask = (thk > 1.0).expand_dims('color', axis=-1)  # add color dimension
    img = np.where(mask, velo_img, topo_img)

    # put blue color below interpolated sea level
    # this does not work because usurf contains no bathymetry
    #sl_interp = np.interp(time[i], sl_time, sl)
    #img[usurf < sl_interp] = (0.776, 0.925, 1, 0)  #c6ecff

    # plot surface elevation
    ax.plot_surface(xx, yy, usurf, vmin=0.0, vmax=3e3, facecolors=img,
                    rstride=1, cstride=1, linewidth=0, alpha=1.0)

    # set axes limits
    ax.set_xlim3d((400e3, 575e3))
    ax.set_ylim3d((5075e3, 5250e3))
    ax.set_zlim3d((-0e3, 9e3))
    ax.set_axis_off()

    # add text tag
    label.set_text('%.1f ka' % age)
    nc.close()

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
