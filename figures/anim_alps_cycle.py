#!/usr/bin/env python2
# coding: utf-8

import os
import util as ut
import multiprocessing as mp


def draw(t):
    """Plot complete figure for given time."""

    # initialize figure
    fig, ax, cax, tsax = ut.pl.subplots_cax_ts_anim(t=t)
    ut.pl.add_signature('J. Seguinot et al. (in prep.)')

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)

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
    ut.pl.add_corner_tag('%.1f ka' % (0.0-t/1e3), ax)

    # add colorbar
    cb = fig.colorbar(im, cax)
    cb.set_label('bedrock uplift (m)')

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

    # return figure
    return fig


def saveframe(years):
    """Independently plot one frame."""

    # check if file exists
    framename = '{:06d}.png'.format(years)
    framepath = '/scratch_net/iceberg/juliens/anim/anim_alps_cycle/' + framename
    if os.path.isfile(framepath):
        return

    # plot
    t = years - 120e3
    print 'plotting at %.1f ka...' % (0.0-t/1e3)
    fig = draw(t)

    # save
    fig.savefig(framepath)
    ut.pl.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""
    dt = 100
    pool = mp.Pool(processes=12)
    pool.map(saveframe, xrange(dt, 120001, dt))
    pool.close()
    pool.join()
