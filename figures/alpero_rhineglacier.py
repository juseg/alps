#!/usr/bin/env python
# Copyright (c) 2020, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Rhine glacier velocity and erosion potential."""

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
        gridspec_kw=dict(left=15, right=15, bottom=22, top=6, wspace=1.5))
    cax1 = fig.add_axes_mm([10.5, 22, 3, 32])
    cax2 = fig.add_axes_mm([163.5, 22, 3, 32])
    pfgrid = fig.subplots_mm(ncols=3, sharex=True, gridspec_kw=dict(
        left=15, right=15, bottom=9, top=39.5, wspace=1.5))

    # set extent and subfig labels
    for ax, label in zip(grid, 'abc'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
        ax.set_extent([410e3, 620e3, 5160e3, 5300e3], crs=ax.projection)

    # Map axes
    # --------

    # open postprocessed output
    with pismx.open.dataset(
                '../data/processed/alpcyc.1km.epic.pp.ex.1ka.nc') as ds:
        ds = ds.sel(age=25)

        # compute sliding magnitude and erosion rates
        sliding = (ds.uvelbase**2+ds.vvelbase**2)**0.5
        her15 = 2.7e-4*sliding**2.02  # (mm/a, Herman et al., 2015)
        coo20 = 1.665e-1*sliding**0.6459  # (mm/a, Cook et al., 2020)

    # plot background topo
    for ax in grid:
        ds.topg.plot.imshow(
            ax=ax, add_colorbar=False, cmap='Greys', vmin=0, vmax=3e3)

    # plot sliding velocity and erosion rates
    sliding.plot.imshow(
        ax=grid[0], alpha=0.75, cbar_ax=cax1, cbar_kwargs=dict(
            label=r'sliding velocity ($m\,a^{-1}$)'),
        cmap='viridis_r', norm=mpl.colors.LogNorm(1e1, 1e3))
    her15.plot.imshow(
        ax=grid[1], add_colorbar=False, alpha=0.75,
        cmap='plasma_r', norm=mpl.colors.LogNorm(1e-2, 1e1))
    coo20.plot.imshow(
        ax=grid[2], alpha=0.75, cbar_ax=cax2, cbar_kwargs=dict(
            format=mpl.ticker.LogFormatterMathtext(),
            label=r'erosion rate ($mm\,a^{-1}$)'),
        cmap='plasma_r', norm=mpl.colors.LogNorm(1e-2, 1e1))

    # add titles
    grid[0].set_title('Seguinot et al. (2018)')
    grid[1].set_title('Herman et al. (2019)')
    grid[2].set_title('Cook et al. (2020)')

    # fix left colorbar label position
    cax1.yaxis.set_ticks_position('left')
    cax1.yaxis.set_label_position('left')

    # add profile line from shapefile
    x, y = cpf.read_shp_coords('../data/native/profile_rhine.shp')
    for ax in grid:
        ax.plot(x, y, color='0.25', dashes=(2, 1))
        ax.plot(x[0], y[0], color='0.25', marker='o')

    # Profiles
    # --------

    # convert distance to km
    x['d'] /= 1e3
    y['d'] /= 1e3

    # interpolate thickness and plot envelope
    sliding.interp(x=x, y=y, method='linear').plot(ax=pfgrid[0], color='C1')
    her15.interp(x=x, y=y, method='linear').plot(ax=pfgrid[1], color='C9')
    coo20.interp(x=x, y=y, method='linear').plot(ax=pfgrid[2], color='C9')

    # set profile axes properties
    pfgrid[0].set_ylabel('sliding\nvelocity\n'+r'($m\,a^{-1}$)', labelpad=3)
    pfgrid[1].set_yticks([])
    pfgrid[2].set_ylim(*pfgrid[1].get_ylim())
    pfgrid[2].yaxis.set_ticks_position('right')
    pfgrid[2].yaxis.set_label_position('right')
    pfgrid[2].set_ylabel('erosion\nrate\n'+r'($mm\,a^{-1}$)', labelpad=10)
    for ax in pfgrid:
        ax.set_title(None)
        ax.set_xlabel('distance along flow (km)')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
