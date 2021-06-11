#!/usr/bin/env python
# Copyright (c) 2020-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion transect evolution."""

import os
import matplotlib as mpl
import cartopy.crs as ccrs
import cartowik.profiletools as cpf
import cartowik.decorations as cde
import absplots as apl
import hyoga.open
import util


def main():
    """Main program called during execution."""

    # erosion law
    law = os.getenv('ALPERO_LAW', 'kop2015')

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 80), ncols=4, sharex=True, sharey=True,
        subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=1.5, right=19, bottom=40.5, top=1.5, wspace=1.5))
    tsax = fig.add_axes_mm([1.5, 9, 177-1.5-19, 30])
    cax = fig.add_axes_mm([177-19+1.5, 40.5, 3, 38])

    # set extent and subfig labels
    for ax, label in zip(grid, 'abcd'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
        ax.set_extent([440e3, 580e3, 5160e3, 5300e3], crs=ax.projection)

    # plot ages and levels for consistency
    ages = [36, 24, 16, 0]
    if law == 'kop2015':
        levels = [10**i for i in range(-9, 1)]
    else:
        levels = [10**i for i in range(-6, 4)]

    # read profile coordinates
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')

    # Map axes
    # --------

    # open postprocessed extra output
    with hyoga.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ex.1ka.nc') as extra:
        pass

    # loop on selected ages
    for ax, age in zip(grid, ages):

        # compute erosion
        ds = extra.sel(age=age)
        sliding = (ds.uvelbase**2+ds.vvelbase**2)**0.5  # (m/a)
        if law == 'kop2015':
            erosion = 5.2e-8*sliding**2.34  # (mm/a, Koppes et al., 2015)
        elif law == 'her2015':
            erosion = 2.7e-4*sliding**2.02  # (mm/a, Herman et al., 2015)
        elif law == 'hum1994':
            erosion = 1e-1*sliding  # (mm/a, Humphrey and Raymond, 1994)
        elif law == 'coo2020':
            erosion = 1.665e-1*sliding**0.6459  # (mm/a, Cook et al., 2020)

        # plot map data
        ds.topg.plot.imshow(
            ax=ax, add_colorbar=False, cmap='Greys', vmin=0, vmax=3e3)
        erosion.plot.contourf(
            ax=ax, add_colorbar=False, alpha=0.75, cmap='YlOrBr',
            levels=levels, extend='both')
        erosion.notnull().plot.contour(
            ax=ax, levels=[0.5], colors='k', linewidths=0.25)

        # add profile line
        ax.plot(x, y, color='0.25', dashes=(2, 1))
        ax.plot(x[0], y[0], color='0.25', marker='o')

        # add age tag
        ax.set_title('')
        util.fig.add_subfig_label('%d ka' % age, ax=ax, ha='right', va='top')

        # add profile axes vertical line
        tsax.axvline(age, color='0.25', dashes=(2, 1))
        tsax.plot(age, 0, color='0.25', marker='o')

    # add scale bar on second panel
    cde.add_scale_bar(grid[0], label='50 km', length=50e3, pad=10e3)

    # Profiles
    # --------

    # plot marine isotope stages
    util.fig.plot_mis(ax=tsax, y=0.9)
    util.fig.add_subfig_label('(e)', ax=tsax)

    # open aggregated output
    with hyoga.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot erosion profile (coarsen to reduce figure size)
        ds = ds.coarsen(age=5).mean()  # 3.7 -> 1.0 MiB
        (ds.assign_coords(d=ds.d/1e3)[law+'_rhin']*1e3).plot.contourf(
            ax=tsax, alpha=0.75, cmap='YlOrBr', levels=levels, x='age', y='d',
            cbar_ax=cax, cbar_kwargs=dict(
                label=r'potential erosion rate ($mm\,a^{-1}$)',
                format=mpl.ticker.LogFormatterMathtext(),
                ticks=levels[::3]))  # (mpl issue #11937)

    # set axes properties
    tsax.set_xlim(120, 0)
    tsax.set_xlabel('age (ka)')
    tsax.set_ylabel('distance along flow (km)')
    tsax.yaxis.set_ticks_position('right')
    tsax.yaxis.set_label_position('right')

    # save figure
    fig.savefig(__file__[:-3] + ('_'+law if law != 'kop2015' else ''))


if __name__ == '__main__':
    main()
