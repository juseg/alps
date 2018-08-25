#!/usr/bin/env python2
# coding: utf-8

import os
import util as ut
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt


# set contour levels, colors and hatches
levs = [1e-1, 1e0, 1e1]
cmap = plt.get_cmap('Blues', len(levs)+1)
cols = cmap(range(len(levs)+1))


def draw(t):
    """Plot complete figure for given time."""

    # initialize figure
    fig, ax, cax, tsax = ut.pl.subplots_cax_ts_anim(dt=False, mis=False)

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)
    x, y, temp = nc._extract_xyz('temppabase', t)
    x, y, slip = nc._extract_xyz('velbase_mag', t)

    # identify problematic areas
    cold = (temp < -1e-3)
    coldslip = np.ma.masked_where(1-cold, slip)
    warmslip = np.ma.masked_where(cold, slip)

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.imshow('velbase_mag', ax, t, norm=ut.pl.velnorm, cmap='Reds', alpha=0.75)
    im = ax.contourf(x, y, coldslip, levels=levs, colors=cols, extend='both', alpha=0.75)
    cs = nc.contour('temppabase', ax, t, levels=[-1e-3], colors='k',
                    linewidths=0.25, linestyles=['-'], zorder=0)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

    # close extra data
    nc.close()

    # add vectors
    ut.pl.draw_natural_earth(ax)
    ut.pl.add_corner_tag('%.1f ka' % (0.0-t/1e3), ax)
    ut.pl.add_signature('J. Seguinot et al. (in prep.)')

    # add colorbar
    cb = fig.colorbar(im, cax, extend='both')
    cb.set_label('cold-based sliding ($m\,a^{-1}$)')

    # plot scatter
    tsax.set_yscale('log')
    tsax.set_xscale('symlog', linthreshx=1e-12)
    tsax.scatter(temp, coldslip, marker='.', c='C1', alpha=0.1)
    tsax.scatter(temp, warmslip, marker='.', c='C5', alpha=0.1)
    tsax.set_xlabel('basal temperature below freezing (K)')
    tsax.set_ylabel('basal velocity ($m\,a^{-1}$)')
    tsax.set_xlim(-5e1, 5e-13)
    tsax.set_ylim(1e-4, 1e4)

    # return figure
    return fig


def saveframe(years):
    """Independently plot one frame."""

    # check if file exists
    framename = '{:06d}.png'.format(years)
    framepath = '/scratch_net/iceberg/juliens/anim/anim_alps_coldslip/' + framename
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
