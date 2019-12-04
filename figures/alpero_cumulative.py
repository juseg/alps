#!/usr/bin/env python
# Copyright (c) 2016-2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion time evolution."""

import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax, cax, tsax = util.fig.subplots_cax_ts()

    # load aggregated data
    # FIXME age coords in preprocessing, open with xarray
    with util.io.open_dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot map data
        glaciated = ds.cumu_erosion > 0.0
        ds.cumu_erosion.where(glaciated).plot.contourf(
            ax=ax, alpha=0.75, cmap='YlOrBr', cbar_ax=cax,
            cbar_kwargs=dict(label='total erosion (m)', format='%g'),
            levels=[10**i for i in range(0, 5)])
        glaciated.plot.contour(ax=ax, colors='k', linewidths=0.5, levels=[0.5])

        # plot time series
        # FIXME replace temperature offset by ice volume
        data = ds.erosion_rate*1e-9
        roll = data.rolling(time=100, center=True).mean()
        twax = tsax.twinx()
        twax.plot(data.age/1e3, data, c='C11', alpha=0.5)
        twax.plot(data.age/1e3, roll, c='C11')
        twax.set_ylabel(r'erosion rate ($km\,a^{-1}$)', color='C11')
        twax.set_xlim(120.0, 0.0)
        twax.set_ylim(-0.5, 3.5)

    # add map elements
    util.pl.draw_boot_topo(ax)
    util.geo.draw_natural_earth(ax)

    # save figure
    util.pl.savefig(fig)


if __name__ == '__main__':
    main()
