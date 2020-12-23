#!/usr/bin/env python
# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion transect evolution."""

import matplotlib as mpl
import cartopy.crs as ccrs
import cartowik.profiletools as cpf
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 80), ncols=3, sharex=True, sharey=True,
        subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=1.5, right=1.5, bottom=40.5, top=1.5, wspace=1.5))
    cax = fig.add_axes_mm([163.5, 9, 3, 30])
    tsax = fig.add_axes_mm([15, 9, 147, 30])

    # set extent and subfig labels
    for ax, label in zip(grid, 'abc'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
        ax.set_extent([410e3, 620e3, 5160e3, 5300e3], crs=ax.projection)

    # plot ages and levels for consistency
    ages = [24, 20, 16]
    levels = [10**i for i in range(-9, 1)]

    # read profile coordinates
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')

    # Map axes
    # --------

    # open postprocessed extra output
    with pismx.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ex.1ka.nc') as extra:
        pass

    # loop on selected ages
    for ax, age in zip(grid, ages):

        # compute erosion
        ds = extra.sel(age=age)
        sliding = (ds.uvelbase**2+ds.vvelbase**2)**0.5  # (m/a)
        erosion = 2.7e-7*sliding**2.02  # (m/a, Herman et al., 2015)

        # plot map data
        ds.topg.plot.imshow(
            ax=ax, add_colorbar=False, cmap='Greys', vmin=0, vmax=3e3)
        erosion.plot.contourf(
            ax=ax, add_colorbar=False, alpha=0.75, cmap='YlOrBr',
            levels=levels)
        erosion.notnull().plot.contour(
            ax=ax, levels=[0.5], colors='k', linewidths=0.25)

        # add profile line
        ax.plot(x, y, color='0.25', dashes=(2, 1))
        ax.plot(x[0], y[0], color='0.25', marker='o')

        # add age tag and vertical line
        ax.set_title('')
        util.fig.add_subfig_label('%d ka' % age, ax=ax, ha='right', va='bottom')
        tsax.axvline(age, color='0.25', dashes=(2, 1))

    # Profiles
    # --------

    # plot marine isotope stages
    util.fig.plot_mis(ax=tsax, y=0.9)
    util.fig.add_subfig_label('(d)', ax=tsax)

    # open aggregated output
    with pismx.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot erosion profile
        ds.assign_coords(d=ds.d/1e3).her2015_rhin.plot.contourf(
            ax=tsax, alpha=0.75, cmap='YlOrBr', levels=levels, x='age', y='d',
            cbar_ax=cax, cbar_kwargs=dict(
                label='erosion rate ($m\\,a^{-1}$)',
                format=mpl.ticker.LogFormatterMathtext(),
                ticks=levels[::9]))  # (mpl issue #11937)

    # set axes properties
    cax.yaxis.set_label_coords(2.5, 0.5)
    tsax.grid()
    tsax.set_xlim(120, 0)
    tsax.set_xlabel('age (ka)')
    tsax.set_ylabel('distance along flow (km)')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
