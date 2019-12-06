#!/usr/bin/env python
# Copyright (c) 2016--2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps cycle high-resolution inputs."""

import numpy as np
import cartopy.crs as ccrs
import absplots as apl
import pismx.open
import util


def subplots(extent='alps', mode='vertical'):
    """Complicated subplots allowing horizontal or vertical mode."""

    # initialize figure
    figw, figh = 177.0, 142.5 if mode == 'horizontal' else 102.0
    fig = apl.figure_mm(figsize=(figw, figh))
    kwargs = dict(squeeze=False, subplot_kw=dict(projection=ccrs.UTM(32)))
    spaces = dict(wspace=1.5, hspace=1.5)

    # prepare two grids in horizontal mode
    if mode == 'horizontal':
        grid1 = fig.subplots_mm(nrows=1, ncols=3, gridspec_kw=dict(
            left=1.5, right=1.5, bottom=103, top=1.5, **spaces), **kwargs)
        grid2 = fig.subplots_mm(nrows=2, ncols=3, gridspec_kw=dict(
            left=1.5, right=1.5, bottom=12, top=53, **spaces), **kwargs)

    # prepare two grids in vertical mode
    else:
        grid1 = fig.subplots_mm(nrows=3, ncols=1, gridspec_kw=dict(
            left=1.5, right=127.5, bottom=1.5, top=1.5, **spaces), **kwargs).T
        grid2 = fig.subplots_mm(nrows=3, ncols=2, gridspec_kw=dict(
            left=64.5, right=15.0, bottom=1.5, top=1.5, **spaces), **kwargs).T

    # merge axes grids
    grid = np.concatenate((grid1, grid2))

    # add colorbar axes  # FIXME implement ax.get_position_mm in absplots
    for ax in grid[[0, 2], :].flat:
        pos = ax.get_position(original=True)  # cf mpl api changes 3.0.0
        if mode == 'horizontal':
            rect = [pos.x0, pos.y0-4.5/figh, pos.x1-pos.x0, 3.0/figh]
        else:
            rect = [pos.x1+1.5/figw, pos.y0, 3.0/figw, pos.y1-pos.y0]
        ax.cax = fig.add_axes(rect)

    # prepare axes
    for ax, label in zip(grid.flat, 'abcdfhegi'):
        util.fig.prepare_map_axes(ax, extent=extent)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)

    # return figure and axes
    return fig, grid


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = subplots()

    # load merged input file
    with pismx.open.dataset('../data/processed/alpcyc.1km.in.nc') as ds:
        thk = ds.thk.where(ds.thk >= 1.0)
        tpg = ds.topg/1e3
        ghf = ds.bheatflx
        air = ds.air_temp-273.15
        pre = ds.precipitation*910.0/12.0
        std = ds.air_temp_sd

        # plot boot topography
        ckw = dict(label='Basal topography (km)', ticks=range(4))
        for ax in grid.flat:
            img = tpg.plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                                  vmin=0.0, vmax=3.0, zorder=-1)
        fig.colorbar(img, grid[0, 1].cax, extend='max', **ckw)  # FIXME cbar_ax

        # plot geothermal flux (provide manual ticks, never use locator_params
        # on colorbar axes, see mpl issue 11937)
        ax = grid[0, 0]
        levs = range(60, 91, 5)
        ckw = dict(label=r'Geothermal flux ($mW\,m^{-2}$)', ticks=levs[::2])
        ghf.plot.contourf(ax=ax, alpha=0.75, cbar_ax=ax.cax, cbar_kwargs=ckw,
                          cmap='PuOr_r', levels=levs)

        # add scale  # FIXME use cartowik tool
        _, east, south, _ = ax.get_extent()
        ax.plot([east-260e3, east-60e3], [south+60e3]*2, 'w|-')
        ax.text(east-160e3, south+90e3, r'100$\,$km', color='w', ha='center',
                fontweight='bold')

        # plot LGM outline
        ax = grid[0, 1]
        util.geo.draw_lgm_outline(ax)

        # plot boot ice thickness
        ax = grid[0, 2]
        ax.set_extent(util.fig.regions['bern'], crs=ax.projection)
        ckw = dict(label='Modern ice thickness (m)', ticks=range(0, 501, 200))
        thk.plot.imshow(ax=ax, alpha=0.75, cbar_ax=ax.cax, cbar_kwargs=ckw,
                        cmap='Blues', vmin=0e2, vmax=5e2)

        # add scale  # FIXME use cartowik tool
        _, east, south, _ = ax.get_extent()
        ax.plot([east-25e3, east-5e3], [south+5e3]*2, 'w|-')
        ax.text(east-15e3, south+7.5e3, r'20$\,$km', color='w', ha='center',
                fontweight='bold')

        # mark inset  # FIXME implement cartowik inset tool?
        west, east, south, _ = ax.get_extent()
        origax = grid[0, 1]
        util.geo.draw_model_domain(origax, 'bern')
        switch = origax.transData - ax.transAxes
        west0, south0 = switch.transform((west, south))
        east0, south0 = switch.transform((east, south))
        kwargs = dict(lw=0.5, clip_on=False, transform=ax.transAxes, zorder=3)
        ax.plot((west0, 0), (south0, 1), 'k--', **kwargs)
        ax.plot((east0, 1), (south0, 1), 'k--', **kwargs)

        # plot standard deviation (force extend='both' or xarray alters colors)
        levs = [2.0+0.5*i for i in range(7)]
        ckw = dict(label=u'PDD SD (°C)', ticks=levs[::2])
        pkw = dict(alpha=0.75, cmap='Purples', extend='both', levels=levs)
        cts = std[0].plot.contourf(ax=grid[1, 0], add_colorbar=False, **pkw)
        cts = std[6].plot.contourf(ax=grid[2, 0], add_colorbar=False, **pkw)
        fig.colorbar(cts, grid[2, 0].cax, **ckw)  # FIXME use xarray cbar_ax?

        # plot air temperature
        levs = range(-10, 21, 5)
        ckw = dict(label=u'Air temperature (°C)', ticks=levs[::2])
        pkw = dict(alpha=0.75, cmap='RdBu_r', extend='both', levels=levs)
        cts = air[0].plot.contourf(ax=grid[1, 1], add_colorbar=False, **pkw)
        cts = air[6].plot.contourf(ax=grid[2, 1], add_colorbar=False, **pkw)
        fig.colorbar(cts, grid[2, 1].cax, **ckw)  # FIXME use xarray cbar_ax?

        # plot precipitation
        levs = range(50, 251, 50)
        ckw = dict(label='Monthly precipitation (mm)', ticks=levs[1::2])
        pkw = dict(alpha=0.75, cmap='Greens', extend='both', levels=levs)
        cts = pre[0].plot.contourf(ax=grid[1, 2], add_colorbar=False, **pkw)
        cts = pre[6].plot.contourf(ax=grid[2, 2], add_colorbar=False, **pkw)
        fig.colorbar(cts, grid[2, 2].cax, **ckw)  # FIXME use xarray cbar_ax?

        # add map elements
        for i, col in enumerate(grid):
            for j, ax in enumerate(col):
                ax = grid[i, j]
                util.com.add_corner_tag(['', 'Jan.', 'July'][i], ax=ax,
                                        va='bottom')
                util.geo.draw_natural_earth(ax)
                ax.set_title('')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
