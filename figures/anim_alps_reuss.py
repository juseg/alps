#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import numpy as np
import multiprocessing as mp
import scipy.interpolate as sinterp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import iceplotlib.cm as icm

# personal colormaps
cols = [(0.0, (0,0,0,0)), (1.0, (0,0,0,1))]  # transparent to black
shademap = mcolors.LinearSegmentedColormap.from_list('shades', cols)
cols = [(0.0, (1,1,1,0)), (1.0, (1,1,1,1))]  # transparent to white
whitemap = mcolors.LinearSegmentedColormap.from_list('whites', cols)
cols = [(0.0, (1,1,1,1)), (0.5, (1,1,1,0)),
        (0.5, (0,0,0,0)), (1.0, (0,0,0,1))]  # white transparent black
shinemap = mcolors.LinearSegmentedColormap.from_list('shines', cols)


def draw(t):
    """Plot complete figure for given time."""

    # initialize figure
    fig, ax = ut.pl.subplots_anim(t=t)
    ut.pl.add_signature(u'J. Seguinot (2018)')

    # set dynamics axes extent
    zf = 1 - ((t+15e3)/25e3)**2  # zoom factor between 0 and 1
    e0 = 415e3, 505e3, 5195e3, 5255e3  # Luzern 90x60 km
    e1 = 400e3, 520e3, 5190e3, 5270e3  # Luzern 120x80 km
    axe = [c0 + (c1-c0)*zf for (c0, c1) in zip(e0, e1)]
    ax.set_extent(axe, crs=ax.projection)

    # create axes coordinates
    cols, rows = [d*254 for d in fig.get_size_inches()]
    axx, axy = ut.pl.coords_from_extent(axe, cols, rows)

    # load SRTM bedrock topography
    srb, sre = ut.io.open_gtif('../data/external/srtm.tif', extent=axe)
    srx, sry = ut.pl.coords_from_extent(sre, *srb.shape[::-1])

    # load boot topo
    filepath = 'input/boot/alps-srtm+thk+gou11simi-1km.nc'
    nc = ut.io.load(filepath)
    bref = nc.variables['topg'][:].T
    nc.close()

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)
    ncx, ncy, ncb = nc._extract_xyz('topg', t)
    ncx, ncy, ncs = nc._extract_xyz('usurf', t)

    # compute bedrock uplift
    ncu = ncb - bref

    # interpolate surfaces to axes coords (interp2d seem faster than interp)
    bi = sinterp.interp2d(srx, sry, srb, kind='quintic')(axx, axy)
    si = sinterp.interp2d(ncx, ncy, ncs, kind='quintic')(axx, axy)
    mi = sinterp.interp2d(ncx, ncy, ncs.mask, kind='quintic')(axx, axy)
    ui = sinterp.interp2d(ncx, ncy, ncu, kind='quintic')(axx, axy)
    mi = (mi > 0.5) + (si < bi)
    si = np.ma.masked_array(si, mi)

    # correct basal topo for uplift
    bi = bi + ui

    # compute relief shading
    kw = dict(extent=axe, altitude=30.0, transparent=True)
    s300 = ut.pl.shading(bi, azimuth=300.0, **kw)
    s315 = ut.pl.shading(bi, azimuth=315.0, **kw)
    s330 = ut.pl.shading(bi, azimuth=330.0, **kw)
    sh = (s300+s315+s330) / 3.0

    # plot interpolated results
    im = ax.imshow(bi, extent=axe, vmin=-3e3, vmax=3e3, cmap=icm.topo, zorder=-1)
    im = ax.imshow(sh, extent=axe, vmin=-1.0, vmax=1.0, cmap=shinemap, zorder=-1)
    cs = ax.contourf(axx, axy, mi, levels=[0.0, 0.5], colors='w', alpha=0.75)
    cs = ax.contour(axx, axy, mi, levels=[0.5], colors='0.25', linewidths=0.25)
    cs = ax.contour(axx, axy, si, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
    cs = ax.contour(axx, axy, si, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)

    # add streamplot
    ss = nc.streamplot('velsurf', ax, t, cmap='Blues', norm=ut.pl.velnorm,
                       density=(12, 8), linewidth=0.5, arrowsize=0.25)

    # close extra data
    nc.close()

    ## add colorbar
    #cb = ut.pl.add_colorbar(ss.lines, cax, extend='both')
    #cb.set_label(r'surface velocity ($m\,a^{-1}$)')

    # add vectors
    ut.pl.draw_swisstopo_hydrology(ax)
    ut.pl.draw_major_cities(ax, maxrank=8)
    ut.pl.draw_lgm_outline(ax, c='#b00000')
    ut.pl.add_corner_tag('%.0f years ago' % (0.0-t), ax)

    # return figure
    return fig


def saveframe(years):
    """Independently plot one frame."""

    # check if file exists
    framepath = os.path.join(os.environ['HOME'], 'anim',
                             os.path.splitext(sys.argv[0])[0],
                             '{:06d}.png'.format(years))
    if os.path.isfile(framepath):
        return

    # plot
    t = years - 120e3
    print 'plotting at %.0f a...' % (0.0-t)
    fig = draw(t)

    # save
    fig.savefig(framepath)
    plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""
    dt = 10
    pool = mp.Pool(processes=12)
    pool.map(saveframe, xrange(80000, 105001, dt))
    pool.join()
