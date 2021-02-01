#!/usr/bin/env python
# Copyright (c) 2020-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Rhine glacier velocity and erosion potential."""

import numpy as np
import cartopy.crs as ccrs
import cartowik.profiletools as cpf
import absplots as apl
import pismx.open
import util

DASHES = dict(
    kop2015=(), her2015=(3, 1, 1, 1), hum1994=(2, 1), coo2020=(1, 1))


def plot_erosion_laws(ax):
    """Plot erosion power laws."""

    # plot power laws (in m/a)
    sliding = np.logspace(0, 4, 5)
    ax.plot(sliding, 5.2e-11*sliding**2.34, c='C11', dashes=DASHES['kop2015'])
    ax.plot(sliding, 2.7e-7*sliding**2.02, c='C11', dashes=DASHES['her2015'])
    ax.plot(sliding, 1e-4*sliding, c='C11', dashes=DASHES['hum1994'])
    ax.plot(sliding, 1.665e-4*sliding**0.6459, c='C11',
            dashes=DASHES['coo2020'])

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
    plax = fig.add_axes_mm([15, 119-1.5-30, 39, 30])
    pfax = fig.add_axes_mm([15+39+15, 119-1.5-30, 177-15-39-15-18, 30])
    grid = fig.subplots_mm(
        ncols=4, subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=15, right=1.5, bottom=38.5, top=41.5, wspace=1.5))
    tsgrid = fig.subplots_mm(ncols=4, sharey=True, gridspec_kw=dict(
        left=15, right=1.5, bottom=9, top=82, wspace=1.5))

    # set extent and subfig labels
    for ax, label in zip([plax]+[pfax]+list(grid)+list(tsgrid), 'abcdefghij'):
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
    for ax in grid:
        util.fig.prepare_map_axes(ax)
        ax.set_extent([440e3, 580e3, 5160e3, 5300e3], crs=ax.projection)

    # load modelled ice volume
    with pismx.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
        slvol = ds.slvol

    # plot erosion laws
    plot_erosion_laws(plax)

    # read profile coords in km
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')
    x = x.assign_coords(d=x.d/1e3)
    y = y.assign_coords(d=y.d/1e3)

    # open postprocessed output
    with pismx.open.dataset(
                '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # for each erosion law
        for ax, tsax, ref in zip(grid, tsgrid, DASHES):

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

            # plot time series
            tsax.plot(slvol, ds[ref+'_rate'], c='C11', alpha=0.5)
            tsax.plot(slvol, ds[ref+'_rate'].rolling(
                age=100, center=True).mean(), c='C11')

            # plot interpolated profile
            interp = ds[ref+'_cumu'].interp(x=x, y=y, method='linear')
            interp.plot(ax=pfax, color='C11', dashes=DASHES[ref],
                        label=ds[ref+'_cumu'].long_name.split(')')[0] + ')')

            # set time series axes properties
            tsax.set_xlabel('ice volume (cm s.l.e.)')
            tsax.set_yscale('log')
            tsax.set_ylim(10**4.3, 10**7.7*1e3)

    # set profile axes properties
    tsgrid[0].set_ylabel(r'volumic erosion rate ($m^3\,a^{-1}$)')
    pfax.set_xlabel('distance along flow (km)')
    pfax.set_ylabel('erosion potential (m)')
    pfax.set_yscale('log')
    pfax.legend()

    # add colorbar
    fig.colorbar(cset, cax=fig.add_axes_mm([177-18+1.5, 119-1.5-30, 3, 30]),
                 label='erosion potential (m)', format='%g')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
