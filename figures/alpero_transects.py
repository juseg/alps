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
        figsize=(177, 60), ncols=3, subplot_kw=dict(projection=ccrs.UTM(32)),
        gridspec_kw=dict(left=1.5, right=15, bottom=23.5, top=1.5, wspace=1.5))
    cax = fig.add_axes_mm([163.5, 22.5, 3, 35])
    pfgrid = fig.subplots_mm(ncols=3, sharey=True, gridspec_kw=dict(
        left=1.5, right=15, bottom=9, top=38, wspace=1.5))

    # read profile coords and convert distance to km
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')
    x.assign_coords(d=x.d/1e3)
    y.assign_coords(d=y.d/1e3)

    # open postprocessed output
    with pismx.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ex.1ka.nc') as extra:
        pass

    # Map axes
    # --------

    # loop on selected ages
    for i, age in enumerate([30, 25, 20]):
        ax = grid[i]

        # prepare map axes
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % 'abc'[i], ax=ax)
        ax.set_extent([410e3, 620e3, 5160e3, 5300e3], crs=ax.projection)

        # compute erosion
        ds = extra.sel(age=age)
        sliding = (ds.uvelbase**2+ds.vvelbase**2)**0.5  # (m/a)
        erosion = 2.7e-7*sliding**2.02  # (m/a, Herman et al., 2015)

        # plot map data
        ds.topg.plot.imshow(
            ax=ax, add_colorbar=False, cmap='Greys', vmin=0, vmax=3e3)
        erosion.plot.contourf(
            ax=ax, add_labels=False, alpha=0.75, cbar_ax=cax, cmap='YlOrBr',
            levels=[10**i for i in range(-9, 1)], cbar_kwargs=dict(
                label='erosion rate ($m\\,a^{-1}$)',
                format=mpl.ticker.LogFormatterMathtext(),
                ticks=[1e-9, 1e-6, 1e-3, 1e0]))  # (mpl issue #11937)
        erosion.notnull().plot.contour(
            ax=ax, levels=[0.5], colors='k', linewidths=0.25)

        # add profile line
        ax.plot(x, y, color='0.25', dashes=(2, 1))
        ax.plot(x[0], y[0], color='0.25', marker='o')
        ax.set_title('')

        # Profiles
        # --------

        # plot interpolated erosion
        ax = pfgrid[i]
        erosion.interp(x=x, y=y, method='linear').plot(ax=ax, color='C11')

        # set axes properties
        ax.set_title('')
        ax.set_xlabel('')
        ax.yaxis.set_ticks_position('right')
        ax.yaxis.set_label_position('right')

    # set axes labels
    pfgrid[1].set_xlabel('distance along flow (km)')
    pfgrid[2].set_ylabel('erosion\nrate\n'+r'($mm\,a^{-1}$)', labelpad=0)

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
