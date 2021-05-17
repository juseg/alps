#!/usr/bin/env python
# Copyright (c) 2020-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion isostatic uplift."""

import cartopy.crs as ccrs
import absplots as apl
import hyoga.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 80), ncols=3, sharex=True, sharey=True,
        subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=1.5, right=1.5, bottom=40.5, top=1.5, wspace=1.5))
    tsax = fig.add_axes_mm([15, 9, 177-30-3-1.5, 30])
    cax = fig.add_axes_mm([177-18+1.5, 9, 3, 30])

    # set extent and subfig labels
    for ax, label in zip(grid, 'abc'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)
    util.fig.add_subfig_label('(d)', ax=tsax)

    # Map axes
    # --------

    # open postprocessed extra output
    with hyoga.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ex.1ka.nc') as extra:

        # compute isostasic uplift
        extra = extra.hyoga.assign_isostasy(
            '../data/processed/alpcyc.1km.in.nc')
        extra['uplift'] = -extra.isostasy.differentiate('age')

        # loop on selected ages
        for ax, age in zip(grid, [12, 8, 4]):

            # plot model output
            ds = extra.sel(age=age)
            ds.hyoga.plot.bedrock_altitude(ax=ax, vmin=0, vmax=4500)
            ds.hyoga.plot.bedrock_isostasy(
                ax=ax, cbar_ax=cax,
                cbar_kwargs=dict(label=r'isostatic depression (m)'),
                levels=[-100, -50, -20, 0, 2, 5, 10], extend='both')
            ds.uplift.plot.contour(
                ax=ax, levels=range(-20, 21), linewidths=0.5, colors='0.25')
            ds.hyoga.plot.ice_margin(ax=ax, edgecolor='none', facecolor='0.5')

            # add age tag and vertical line
            ax.set_title('')
            util.fig.add_subfig_label(
                '%d ka' % age, ax=ax, ha='right', va='bottom')
            tsax.axvline(age, color='0.25', dashes=(2, 1))

    # Time series
    # -----------

    # open aggregated output
    with hyoga.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        dep = ds.volumic_lift / (600e3*900e3)  # m3 / m2 = m
        uplift = -dep.differentiate('age')
        uplift.plot(ax=tsax, color='tab:green', alpha=0.25)
        # smooth out model restart artefacts
        dep = dep.where(ds.age % 0.5 != 0)
        uplift = -dep.differentiate('age')  # m / ka = mm a-1
        uplift.plot(ax=tsax, color='tab:green')

    # set axes properties
    tsax.set_rasterization_zorder(2.5)
    tsax.set_xlim(18, 0)
    tsax.set_ylim(-1, 16)
    tsax.set_xlabel('age (ka)')
    tsax.set_ylabel(r'mean uplift rate ($mm\,a^{-1}$)')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
