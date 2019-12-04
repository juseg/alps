#!/usr/bin/env python
# coding: utf-8

import os
import sys
import util
import multiprocessing as mp
import matplotlib.pyplot as plt


def draw(t):
    """Plot complete figure for given time."""

    # initialize figure
    fig, ax, cax, tsax = util.fi.subplots_cax_ts_anim(t=t)
    util.pl.add_signature('J. Seguinot et al. (2018)')

    # load extra data
    filepath = util.alpcyc_bestrun + 'y???????-extra.nc'
    nc = util.io.load(filepath)

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.imshow('velsurf_mag', ax, t, norm=util.pl.velnorm, cmap='Blues', alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=util.pl.inlevs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=util.pl.utlevs,
                    colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

    # close extra data
    nc.close()

    # add vectors
    util.ne.draw_natural_earth(ax)
    util.na.draw_lgm_outline(ax)
    util.pl.draw_footprint(ax)
    util.pl.add_corner_tag('%.1f ka' % (0.0-t/1e3), ax)

    # add colorbar
    cb = util.pl.add_colorbar(im, cax, extend='both')
    cb.set_label(r'surface velocity ($m\,a^{-1}$)')

    # load time series data
    filepath = util.alpcyc_bestrun + 'y???????-ts.nc'
    nc = util.io.load(filepath)
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # plot time series
    mask = age>=-t/1e3
    tsax = tsax.twinx()
    tsax.plot(age[mask], vol[mask], c='C1')
    tsax.set_ylabel('ice volume (m s.l.e.)', color='C1')
    tsax.set_xlim(120.0, 0.0)
    tsax.set_ylim(-0.05, 0.35)
    tsax.locator_params(axis='y', nbins=6)
    tsax.grid(axis='y')

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
