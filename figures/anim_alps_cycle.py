#!/usr/bin/env python2
# coding: utf-8

import os
import util as ut
import multiprocessing as mp

def plot_map(fig, ax, cax, t):
    """Plot map at given time."""

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)
    time = nc.variables['time'][:]/(365.0*24*60*60)

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.imshow('velsurf_mag', ax, t, norm=ut.pl.velnorm, cmap='Blues', alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs,
                    colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

    # close extra data
    nc.close()

    # add vectors
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_lgm_outline(ax)
    ut.pl.draw_footprint(ax)
    ut.pl.add_corner_tag('%.2f ka' % (-t/1e3), ax)

    # add colorbar
    cb = fig.colorbar(im, cax, extend='both')
    cb.set_label(r'surface velocity ($m\,a^{-1}$)')


def plot_ts(tsax, t):
    """Plot timeseries until given time."""

    # load time series data
    filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # plot time series
    mask = age>=-t/1e3
    tsax = tsax.twinx()
    tsax.plot(age[mask], vol[mask], c=ut.pl.palette['darkblue'])
    tsax.set_ylabel('ice volume (m s.l.e.)', color=ut.pl.palette['darkblue'])
    tsax.set_xlim(120.0, 0.0)
    tsax.set_ylim(-0.05, 0.35)
    tsax.locator_params(axis='y', nbins=6)
    tsax.grid(axis='y')


def saveframe(age):
    """Independently plot one frame."""

    # check if file exists
    framepath = '/scratch_net/iceberg/juliens/anim/anim_alps_cycle/%06d.png' % age
    if os.path.isfile(framepath):
        return

    # initialize figure
    fig, ax, cax, tsax = ut.pl.subplots_cax_ts_anim()
    ut.pl.add_signature('J. Seguinot et al. (in prep.)')

    # plot
    print 'plotting at %.2f ka...' % (age/1e3)
    plot_map(fig, ax, cax, -age)
    plot_ts(tsax, -age)

    # save
    fig.savefig(framepath)
    ut.pl.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""
    pool = mp.Pool(processes=12)
    pool.map(saveframe, xrange(0, 120000, 100))
    pool.close()
    pool.join()
