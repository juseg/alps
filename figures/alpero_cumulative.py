#!/usr/bin/env python
# Copyright (c) 2016-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion cumulative."""

import os
import hyoga.open
import cartowik.decorations as cde
import util


def main():
    """Main program called during execution."""

    # erosion law
    law = os.getenv('ALPERO_LAW', 'kop2015')

    # initialize figure
    fig, ax, cax, tsax = util.fig.subplots_cax_ts(dt=False)

    # load aggregated data
    with hyoga.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot map data
        midlev = 0 if law == 'kop2015' else 2
        ds[law+'_cumu'].plot.contourf(
            ax=ax, alpha=0.75, cmap='YlOrBr', cbar_ax=cax,
            cbar_kwargs=dict(label='cumulative erosion potential (m)', format='%g'),
            levels=[10**i for i in range(midlev-2, midlev+3)])
        ds[law+'_cumu'].notnull().plot.contour(
            ax=ax, colors='k', linewidths=0.5, levels=[0.5])

    # add map elements
    util.geo.draw_boot_topo(ax)
    util.geo.draw_natural_earth(ax)
    util.geo.draw_lgm_outline(ax, edgecolor='C1')
    cde.add_scale_bar(ax, label='100 km', length=100e3, pad=220e3)

    # plot time series
    util.ero.plot_series(ax=tsax, law=law)

    # save figure
    fig.savefig(__file__[:-3] + ('_'+law if law != 'kop2015' else ''))


if __name__ == '__main__':
    main()
