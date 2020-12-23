#!/usr/bin/env python
# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Rhine glacier velocity and erosion potential."""

import cartopy.crs as ccrs
import cartowik.profiletools as cpf
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 81), ncols=3, subplot_kw=dict(projection=ccrs.UTM(32)),
        gridspec_kw=dict(left=1.5, right=1.5, bottom=41.5, top=1.5,
                         wspace=1.5))
    caxgrid = fig.subplots_mm(ncols=3, gridspec_kw=dict(
        left=1.5, right=1.5, bottom=36.6, top=41, wspace=1.5))
    tsax = fig.add_axes_mm([12, 9, 177-12-1.5, 18])

    # set extent and subfig labels
    for ax, label in zip(grid, 'abc'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
        ax.set_extent([410e3, 620e3, 5160e3, 5300e3], crs=ax.projection)

    # read profile coords in km
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')
    x = x.assign_coords(d=x.d/1e3)
    y = y.assign_coords(d=y.d/1e3)

    # open postprocessed output
    with pismx.open.dataset(
                '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # for each erosion law
        for ax, cax, ref, lev in zip(
                grid, caxgrid, ['coo2020', 'her2015', 'kop2015'], [-1, 0, -2]):

            # plot cumulative erosion
            authors = ds[ref+'_cumu'].long_name.split(')')[0] + ')'
            ds[ref+'_cumu'].plot.contourf(
                alpha=0.75, ax=ax, cmap='YlOrBr', cbar_ax=cax,
                levels=[10**i for i in range(lev, lev+5)], cbar_kwargs=dict(
                    label='erosion potential (m) after '+authors,
                    format='%g', orientation='horizontal'))

            # plot background topo and ice margin
            util.geo.draw_boot_topo(ax)
            ds[ref+'_cumu'].notnull().plot.contour(
                ax=ax, levels=[0.5], colors='k', linewidths=0.25)

            # add profile line from shapefile
            ax.plot(x, y, color='0.25', dashes=(2, 1))
            ax.plot(x[0], y[0], color='0.25', marker='o')

            # plot interpolated profile
            interp = ds[ref+'_cumu'].interp(x=x, y=y, method='linear')
            interp.plot(ax=tsax, color='C11')
            tsax.text(-2, interp[0], authors, color='C11', ha='right')

    # set profile axes properties
    tsax.set_xlim(-40, 220)
    tsax.set_xlabel('distance along flow (km)')
    tsax.set_ylabel('erosion potential (m)')
    tsax.set_yscale('log')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
