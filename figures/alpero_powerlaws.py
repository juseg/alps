#!/usr/bin/env python
# Copyright (c) 2020-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Rhine glacier velocity and erosion potential."""

import numpy as np
import cartopy.crs as ccrs
import cartowik.profiletools as cpf
import absplots as apl
import hyoga.open
import util


def plot_erosion_laws(ax):
    """Plot erosion power laws."""

    # plot power laws (in m/a)
    sliding = np.logspace(0, 4, 5)
    ax.plot(sliding, 5.2e-11*sliding**2.34, c='C11')
    ax.plot(sliding, 2.7e-7*sliding**2.02, c='C11')
    ax.plot(sliding, 1e-4*sliding, c='C11')
    ax.plot(sliding, 1.665e-4*sliding**0.6459, c='C11')

    # set axes properties
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'sliding velocity ($m\,a^{-1}$)')
    ax.set_ylabel(r'erosion rate ($m\,a^{-1}$)')
    ax.set_ylim(10**-5.2, 10**-0.8)


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(177, 119))
    grid = fig.subplots_mm(
        ncols=4, subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=15, right=1.5, bottom=75.5, top=4.5, wspace=1.5))
    tsgrid = fig.subplots_mm(
        ncols=4, nrows=2, sharex='row', sharey='row', gridspec_kw=dict(
            left=15, right=1.5, bottom=9, top=45, hspace=9, wspace=1.5))
    cax = fig.add_axes_mm([10.5, 75.5, 3, 39])

    # set extent and subfig labels
    for ax, label in zip(list(grid)+list(tsgrid.flat), 'abcdefghijkl'):
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
    for ax in grid:
        util.fig.prepare_map_axes(ax)
        ax.set_extent([440e3, 580e3, 5160e3, 5300e3], crs=ax.projection)

    # load modelled ice volume
    with hyoga.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
        slvol = ds.slvol

    # read profile coords in km
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')
    x = x.assign_coords(d=x.d/1e3)
    y = y.assign_coords(d=y.d/1e3)

    # open postprocessed output
    with hyoga.open.dataset(
                '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # for each erosion law
        for ax, pfax, tsax, ref in zip(
                grid, *tsgrid, ['kop2015', 'her2015', 'hum1994', 'coo2020']):

            # plot cumulative erosion
            cset = ds[ref+'_cumu'].plot.contourf(
                ax=ax, add_colorbar=False, alpha=0.75, cmap='YlOrBr',
                extend='both', levels=[10**i for i in range(-2, 5)])

            # plot background topo and ice margin
            util.geo.draw_boot_topo(ax)
            ds[ref+'_cumu'].notnull().plot.contour(
                ax=ax, levels=[0.5], colors='k', linewidths=0.25)

            # add profile line from shapefile
            ax.plot(x, y, color='0.25', dashes=(2, 1))
            ax.plot(x[0], y[0], color='0.25', marker='o')

            # authors name as title
            ax.set_title(ds[ref+'_cumu'].long_name.split(')')[0] + ')')

            # plot interpolated profile
            ds[ref+'_cumu'].interp(x=x, y=y, method='linear').plot(
                ax=pfax, color='C11')

            # set profile axes properties
            pfax.set_xlabel('distance along flow (km)')
            pfax.set_ylabel('')
            pfax.set_yscale('log')

            # plot time series
            tsax.plot(slvol*100, ds[ref+'_rate'], c='C11', alpha=0.5)
            tsax.plot(slvol*100, ds[ref+'_rate'].rolling(
                age=100, center=True).mean(), c='C11')

            # set time series axes properties
            tsax.set_xlabel('ice volume (cm s.l.e.)')
            tsax.set_yscale('log')
            tsax.set_ylabel('')
            tsax.set_ylim(10**4.5, 10**10.5)

    # add y-labels on leftmost axes
    tsgrid[0, 0].set_ylabel('erosion potential (m)')
    tsgrid[1, 0].set_ylabel(r'annual erosion volume ($m^3 a^{-1}$)')

    # add colorbar
    fig.colorbar(cset, cax=cax, format='%g', pad=-10)
    cax.yaxis.set_ticks_position('left')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
