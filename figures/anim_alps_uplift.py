#!/usr/bin/env python2
# coding: utf-8

import os
import sys
import util as ut
import multiprocessing as mp
import matplotlib.pyplot as plt


# uplift contour levels and colors
levs = [-100.0, -50.0, -20.0, 0.0, 2.0, 5.0, 10.0]
cmap = plt.get_cmap('PRGn_r', len(levs)+1)
cols = cmap(range(len(levs)+1))


def get_depression_ts():
    """Compute depression time-series. This need to be done once and for all
    in order to avoid a memory error."""

    # load boot topo
    filepath = 'input/boot/alps-srtm+thk+gou11simi-1km.nc'
    nc = ut.io.load(filepath)
    zref = nc.variables['topg'][:].T
    nc.close()

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    z = nc.variables['topg'][:]
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    nc.close()

    # compute bedrock depression time series
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    dep = (zref-z).sum(axis=(1, 2))*dx*dy*1e-12

    # return exra age and depression series
    return age, dep


def draw(t):
    """Plot complete figure for given time."""

    # initialize figure
    fig, ax, cax, tsax = ut.pl.subplots_cax_ts_anim(dt=False)
    ut.pl.add_signature('J. Seguinot et al. (in prep.)')

    # load boot topo
    filepath = 'input/boot/alps-srtm+thk+gou11simi-1km.nc'
    nc = ut.io.load(filepath)
    zref = nc.variables['topg'][:].T
    nc.close()

    # load extra data
    filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
    nc = ut.io.load(filepath)

    # plot
    x, y, z = nc._extract_xyz('topg', t)
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = ax.contourf(x, y, z-zref, levels=levs, extend='both',
                     colors=cols, alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs,
                    colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

    # locate maximum depression    
    i = (z-zref).argmin() / z.shape[-1]
    j = (z-zref).argmin() % z.shape[-1]
    maxdep = (zref-z)[i, j]
    c = 'w' if maxdep > -levs[1] else 'k'
    ax.plot(x[j], y[i], 'o', c=c, alpha=0.75)
    ax.text(x[j]+5e3, y[i]+5e3, '{:.0f} m'.format(maxdep), color=c)

    # close extra data
    nc.close()

    # add vectors
    ut.pl.draw_natural_earth(ax)
    ut.pl.add_corner_tag('%.1f ka' % (0.0-t/1e3), ax)

    # add colorbar
    cb = fig.colorbar(im, cax)
    cb.set_label(r'bedrock uplift (m)', labelpad=0)

    # load time series data
    filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][:]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][:]
    nc.close()

    # plot time series
    mask = age>=-t/1e3
    tsax.plot(age[mask], vol[mask], c='0.25')
    tsax.set_ylabel('ice volume (m s.l.e.)', color='0.25')
    tsax.set_ylim(-0.05, 0.35)
    tsax.locator_params(axis='y', nbins=6)
    tsax.grid(axis='y')

    # plot bedrock depression time series
    mask = exage>=-t/1e3
    twax = tsax.twinx()
    twax.plot(exage[mask], exdep[mask], c=ut.pl.palette['darkgreen'])
    twax.set_xlim(120.0, 0.0)
    twax.set_ylim(-5.0, 35.0)
    twax.set_ylabel('volumic depression ($10^{3}\,km^{3}$)')

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

    # compute depression time-series
    print 'computing depression time-series...'
    exage, exdep = get_depression_ts()

    # plot in parallel
    dt = 100
    pool = mp.Pool(processes=12)
    pool.map(saveframe, xrange(dt, 120001, dt))
    pool.close()
    pool.join()
