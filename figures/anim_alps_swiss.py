#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import multiprocessing as mp
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
    fig, ax, cax = ut.pl.subplots_cax_anim_1609(t=t)
    ut.pl.add_signature(u'© J. Seguinot (2018)')

    # set dynamics axes extent
    zf = 1 - (t/120e3)**2  # zoom factor between 0 and 1
    coords0 = 400e3, 448e3, 5128e3, 5155e3  # Bernese Alps 48x27 km
    coords1 = 150e3, 630e3, 5052e3, 5322e3  # Northwestern 480x270 km
    extent = [c0 + (c1-c0)*zf for (c0, c1) in zip(coords0, coords1)]
    ax.set_extent(extent, crs=ax.projection)

    # plot SRTM shaded relief
    z, extent = ut.io.open_gtif('../data/external/srtm.tif', extent=extent)
    s300 = ut.pl.shading(z, extent=extent, azimuth=300.0, altitude=30.0, transparent=True)
    s315 = ut.pl.shading(z, extent=extent, azimuth=315.0, altitude=30.0, transparent=True)
    s330 = ut.pl.shading(z, extent=extent, azimuth=330.0, altitude=30.0, transparent=True)
    s = (s300+s315+s330) / 3.0
    im = ax.imshow(z, extent=extent, vmin=-3e3, vmax=3e3, cmap=icm.topo,
                   interpolation='bilinear', zorder=-1)
    im = ax.imshow(s, extent=extent, vmin=-1.0, vmax=1.0, cmap=shinemap,
                   interpolation='bilinear', zorder=-1)

    # add vectors
    ut.pl.draw_natural_earth_color(ax, countries=True)
    ut.pl.draw_major_cities(ax, maxrank=8)
    ut.pl.draw_lgm_outline(ax, c='#b00000')
    ut.pl.add_corner_tag('%.1f ka' % (0.0-t/1e3), ax)

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)

    # plot
    cs = nc.icemarginf(ax, t, colors='w', alpha=0.75)
    cs = nc.icemargin(ax, t, colors='0.25', linewidths=0.25)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs,
                    colors='0.25', linewidths=0.25)
    ss = nc.streamplot('velsurf', ax, t, velth=1.0,
                       cmap='Blues', norm=ut.pl.velnorm,
                       density=(12, 6.75), linewidth=0.5, arrowsize=0.25)

    # add colorbar
    cb = ut.pl.add_colorbar(ss.lines, cax, extend='both')
    cb.set_label(r'surface velocity ($m\,a^{-1}$)')

    # close extra data
    nc.close()

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
    print 'plotting at %.1f ka...' % (0.0-t/1e3)
    fig = draw(t)

    # save
    fig.savefig(framepath)
    plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""
    dt = 100
    pool = mp.Pool(processes=12)
    pool.map(saveframe, xrange(dt, 120001, dt))
    pool.close()
    pool.join()
