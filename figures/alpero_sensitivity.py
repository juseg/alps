#!/usr/bin/env python
# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion sensibility to climate scenario."""

import cartopy.crs as ccrs
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 85), nrows=2, ncols=3, sharex=True, sharey=True,
        subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=1.5, right=1.5, bottom=1.5, top=6.0, hspace=1.5, wspace=1.5))
    cax = fig.add_axes_mm([177/2-10, 41+9, 20, 3])
    for ax, label in zip(grid.flat, 'abcdef'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)

    # for each record
    for i, rec in enumerate(util.alpcyc_records):
        label = util.alpcyc_clabels[i]
        conf = util.alpcyc_configs[i]
        ax = grid.T.flat[i]

        # load aggregated data
        with pismx.open.dataset(
                '../data/processed/alpero.2km.{}.{}.agg.nc'.format(
                    rec.lower()[:4], ('cp', 'pp')['pp' in conf])) as ds:

            # plot map data
            ds.cumu_erosion.plot.contourf(
                ax=ax, alpha=0.75, cmap='YlOrBr', cbar_ax=cax,
                levels=[10**i for i in range(0, 5)], cbar_kwargs=dict(
                    label='total erosion (m)', format='%g',
                    orientation='horizontal', ticks=[1, 100, 10000]))
            ds.cumu_erosion.notnull().plot.contour(
                ax=ax, colors='k', linewidths=0.5, levels=[0.5])

        # add map elements
        util.geo.draw_boot_topo(ax=ax, filename='alpcyc.2km.in.nc')
        util.geo.draw_natural_earth(ax)

        # set title
        util.com.add_corner_tag(label, ax=ax, va='bottom')
        if i % 2 == 0:
            ax.set_title(rec, fontweight='bold')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
