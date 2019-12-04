#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, grid = util.fi.subplots_inputs()

# load merged input file
with util.io.open_dataset('../data/processed/alpcyc.1km.in.nc') as ds:
    thk = ds.thk.where(ds.thk>=1.0)
    tpg = ds.topg/1e3
    ghf = ds.bheatflx
    air = ds.air_temp-273.15
    pre = ds.precipitation*910.0/12.0
    std = ds.air_temp_sd

    # plot boot topography
    ckw = dict(label='Basal topography (km)', ticks=range(4))
    for ax in grid.flat:
        im = tpg.plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                             vmin=0.0, vmax=3.0, zorder=-1)
    fig.colorbar(im, grid[0, 1].cax, extend='max', **ckw)

    # plot geothermal flux (provide manual ticks, never use locator_params on
    # colorbar axes, see mpl issue 11937)
    ax = grid[0, 0]
    levs = range(60, 91, 5)
    ckw = dict(label='Geothermal flux ($mW\,m^{-2}$)', ticks=levs[::2])
    ghf.plot.contourf(ax=ax, alpha=0.75, cbar_ax=ax.cax, cbar_kwargs=ckw,
                      cmap='PuOr_r', levels=levs)

    # add scale
    w, e, s, n = ax.get_extent()
    ax.plot([e-260e3, e-60e3], [s+60e3]*2, 'w|-')
    ax.text(e-160e3, s+90e3, r'100$\,$km', color='w', ha='center', fontweight='bold')

    # plot LGM outline
    ax = grid[0, 1]
    util.na.draw_lgm_outline(ax)

    # plot boot ice thickness
    ax = grid[0, 2]
    ax.set_extent(util.fi.regions['bern'], crs=ax.projection)
    ckw = dict(label='Modern ice thickness (m)', ticks=range(0, 501, 200))
    thk.plot.imshow(ax=ax, alpha=0.75, cbar_ax=ax.cax, cbar_kwargs=ckw,
                                       cmap='Blues', vmin=0e2, vmax=5e2)

    # add scale
    w, e, s, n = ax.get_extent()
    ax.plot([e-25e3, e-5e3], [s+5e3]*2, 'w|-')
    ax.text(e-15e3, s+7.5e3, r'20$\,$km', color='w', ha='center', fontweight='bold')

    # mark inset
    origax = grid[0, 1]
    util.pl.draw_model_domain(origax, 'bern')
    switch = origax.transData - ax.transAxes
    w0, s0 = switch.transform((w, s))
    e0, s0 = switch.transform((e, s))
    kwargs = dict(lw=0.5, clip_on=False, transform=ax.transAxes, zorder=3)
    ax.plot((w0, 0), (s0, 1), 'k--', **kwargs)
    ax.plot((e0, 1), (s0, 1), 'k--', **kwargs)

    # plot standard deviation (force extend='both' or xarray alters colors)
    levs = [2.0+0.5*i for i in range(7)]
    ckw = dict(label=u'PDD SD (°C)', ticks=levs[::2])
    pkw = dict(alpha=0.75, cmap='Purples', extend='both', levels=levs)
    cs = std[0].plot.contourf(ax=grid[1, 0], add_colorbar=False, **pkw)
    cs = std[6].plot.contourf(ax=grid[2, 0], add_colorbar=False, **pkw)
    fig.colorbar(cs, grid[2, 0].cax, **ckw)

    # plot air temperature
    levs = range(-10, 21, 5)
    ckw = dict(label=u'Air temperature (°C)', ticks=levs[::2])
    pkw = dict(alpha=0.75, cmap='RdBu_r', extend='both', levels=levs)
    cs = air[0].plot.contourf(ax=grid[1, 1], add_colorbar=False, **pkw)
    cs = air[6].plot.contourf(ax=grid[2, 1], add_colorbar=False, **pkw)
    fig.colorbar(cs, grid[2, 1].cax, **ckw)

    # plot precipitation
    levs = range(50, 251, 50)
    ckw = dict(label='Monthly precipitation (mm)', ticks=levs[1::2])
    pkw = dict(alpha=0.75, cmap='Greens', extend='both', levels=levs)
    cs = pre[0].plot.contourf(ax=grid[1, 2], add_colorbar=False, **pkw)
    cs = pre[6].plot.contourf(ax=grid[2, 2], add_colorbar=False, **pkw)
    fig.colorbar(cs, grid[2, 2].cax, **ckw)

    # add map elements
    for i, col in enumerate(grid):
        for j, ax in enumerate(col):
            ax = grid[i, j]
            util.pl.add_corner_tag(['', 'Jan.', 'July'][i], ax=ax, va='bottom')
            util.ne.draw_natural_earth(ax)
            ax.set_title('')

# save
util.pl.savefig()
