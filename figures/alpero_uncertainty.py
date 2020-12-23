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

    # Map axes
    # --------

    # open postprocessed output
    with pismx.open.dataset(
                '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot erosion rates
        ds.coo2020_cumu.plot.contourf(
            alpha=0.75, ax=grid[0], cmap='YlOrBr', cbar_ax=caxgrid[0],
            levels=[10**i for i in range(1, 6)], cbar_kwargs=dict(
                label='total erosion after (m) after Cook et al. (2020)',
                format='%g', orientation='horizontal'))
        ds.her2015_cumu.plot.contourf(
            alpha=0.75, ax=grid[1], cmap='YlOrBr', cbar_ax=caxgrid[1],
            levels=[10**i for i in range(0, 5)], cbar_kwargs=dict(
                label='total erosion after (m) after Herman et al. (2015)',
                format='%g', orientation='horizontal'))
        ds.kop2015_cumu.plot.contourf(
            alpha=0.75, ax=grid[2], cmap='YlOrBr', cbar_ax=caxgrid[2],
            levels=[10**i for i in range(-2, 3)], cbar_kwargs=dict(
                label='total erosion after (m) after Koppes et al. (2015)',
                format='%g', orientation='horizontal'))

    # plot background topo and ice margin
    for ax in grid:
        util.geo.draw_boot_topo(ax)
        ds.her2015_cumu.notnull().plot.contour(
            ax=ax, levels=[0.5], colors='k', linewidths=0.25)

    # add titles
    grid[0].set_title('Seguinot et al. (2018)')
    grid[1].set_title('Herman et al. (2015)')
    grid[2].set_title('Cook et al. (2020)')

    # add profile line from shapefile
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')
    for ax in grid:
        ax.plot(x, y, color='0.25', dashes=(2, 1))
        ax.plot(x[0], y[0], color='0.25', marker='o')

    # Profiles
    # --------

    # convert distance to km
    x = x.assign_coords(d=x.d/1e3)
    y = y.assign_coords(d=y.d/1e3)

    # interpolate thickness and plot envelope
    for ref, label in dict(coo2020='Cook et al., (2020)',
                           her2015='Herman et al. (2015)',
                           kop2015='Koppes et al. (2015)').items():
        interp = ds[ref+'_cumu'].interp(x=x, y=y, method='linear')
        interp.plot(ax=tsax, color='C11')
        last = interp.dropna(dim='d')[-1]
        tsax.text(last.d+5, last, label, color='C11')

    # set profile axes properties
    tsax.set_xlim(-10, 260)
    tsax.set_xlabel('distance along flow (km)')
    tsax.set_ylabel('total erosion (m)')
    tsax.set_yscale('log')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
