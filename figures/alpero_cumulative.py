#!/usr/bin/env python
# Copyright (c) 2016-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion cumulative."""

import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax, cax, tsax = util.fig.subplots_cax_ts(dt=False)

    # load aggregated data
    with pismx.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot map data
        ds.cumu_erosion.plot.contourf(
            ax=ax, alpha=0.75, cmap='YlOrBr', cbar_ax=cax,
            cbar_kwargs=dict(label='total erosion (m)', format='%g'),
            levels=[10**i for i in range(0, 5)])
        ds.cumu_erosion.notnull().contour(
            ax=ax, colors='k', linewidths=0.5, levels=[0.5])

    # add map elements
    util.geo.draw_boot_topo(ax)
    util.geo.draw_natural_earth(ax)

    # plot time series
    util.ero.plot_series(ax=tsax)

    # save figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
