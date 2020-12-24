#!/usr/bin/env python
# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Rhine glacier velocity and erosion potential."""

import numpy as np
import cartopy.crs as ccrs
import cartowik.profiletools as cpf
import absplots as apl
import pismx.open
import util


def plot_erosion_laws(ax):
    """Plot erosion power laws."""

    # plot power laws (in m/a)
    sliding = np.logspace(0, 4, 5)
    ax.plot(sliding, 1.665e-4*sliding**0.6459, c='C11', dashes=(2, 1))
    ax.plot(sliding, 2.7e-7*sliding**2.02, c='C11')
    ax.plot(sliding, 5.2e-11*sliding**2.34, c='C11', dashes=(1, 2))

    # set axes properties
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'sliding velocity ($m\,a^{-1}$)')
    ax.set_ylabel(r'erosion rate ($m\,a^{-1}$)')
    ax.set_ylim(10**-5.2, 10**-0.8)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 80), ncols=3, subplot_kw=dict(projection=ccrs.UTM(32)),
        gridspec_kw=dict(left=1.5, right=1.5, bottom=40.5, top=1.5,
                         wspace=1.5))
    plax = fig.add_axes_mm([15, 9, 30, 30])
    tsax = fig.add_axes_mm([60, 9, 177-60-18, 30])
    cax = fig.add_axes_mm([177-18+1.5, 9, 3, 30])

    # set extent and subfig labels
    for ax, label in zip(grid, 'abc'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
        ax.set_extent([410e3, 620e3, 5160e3, 5300e3], crs=ax.projection)
    util.fig.add_subfig_label('(d)', ax=plax)
    util.fig.add_subfig_label('(e)', ax=tsax)

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
        for ax, ref, dashes in zip(grid, ['coo2020', 'her2015', 'kop2015'],
                                   [(2, 1), (), (1, 2)]):

            # plot cumulative erosion
            authors = ds[ref+'_cumu'].long_name.split(')')[0] + ')'
            cset = ds[ref+'_cumu'].plot.contourf(
                ax=ax, add_colorbar=False, alpha=0.75, cmap='YlOrBr',
                extend='both', levels=[10**i for i in range(-1, 5)])

            # plot background topo and ice margin
            util.geo.draw_boot_topo(ax)
            ds[ref+'_cumu'].notnull().plot.contour(
                ax=ax, levels=[0.5], colors='k', linewidths=0.25)

            # add profile line from shapefile
            ax.plot(x, y, color='0.25', dashes=(2, 1))
            ax.plot(x[0], y[0], color='0.25', marker='o')

            # plot interpolated profile
            interp = ds[ref+'_cumu'].interp(x=x, y=y, method='linear')
            interp.plot(ax=tsax, color='C11', dashes=dashes, label=authors)

    # set profile axes properties
    tsax.set_xlabel('distance along flow (km)')
    tsax.set_ylabel('erosion potential (m)')
    tsax.set_yscale('log')
    tsax.legend()

    # add colorbar
    fig.colorbar(cset, cax=cax, label='erosion potential (m)', format='%g')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
