#!/usr/bin/env python
# Copyright (c) 2016-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import os.path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import multiprocessing as mp

import cartowik.conventions as ccv
import pismx.open


# meshing stride
stride = 1

def draw(i, ax, nc, label):
    """What to draw at each animation step."""

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

    # clear axes
    age = nc.age.squeeze()
    ax.cla()

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
    ax.set_zlim3d((-6e3, 9e3))
    ax.set_axis_off()

    # add text tag
    label.set_text('%.1f ka' % age)


def saveframe(i):
    """Independently plot one frame."""

    # load specmap data
    #filepath = ('input/dsl/specmap.nc')
    #nc = util.io.load(filepath)
    #sl_time = nc.variables['time'][:]
    #sl = nc.variables['delta_SL'][:]
    #nc.close()

    # check if file exists
    framepath = '/run/media/julien/coldroom/anim/alpcyc_3d/%04d.png' % (i+1)
    if os.path.isfile(framepath):
        return

    # load extra data
    filename = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.{:07.0f}.nc'
    nc = pismx.open.subdataset(filename, time=-120000+10+10*i, shift=120000)

    # initialize figure
    fig = plt.figure(0, (135/25.4, 80/25.4))
    ax = fig.add_axes([0, 0, 1, 1], projection='3d')
    ax.view_init(azim=165, elev=30)
    label = fig.text(0.05, 0.90, '', bbox=dict(ec='k', fc='w'))

    # draw and save
    draw(i, ax, nc, label)
    fig.savefig(framepath)
    nc.close()
    plt.close(fig)

# plot individual frames in parallel
pool = mp.Pool(processes=16)
pool.map(saveframe, range(999, 12000, 1000))
pool.close()
pool.join()
