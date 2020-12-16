#!/usr/bin/env python
# Copyright (c) 2016-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion cumulative erosion."""

import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax, cax, tsax = util.fig.subplots_cax_ts(dt=False)

    # plot ice volume time series
    with pismx.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:

        # plot time series
        tsax.plot(ds.age, ds.slvol, c='0.25')
        tsax.set_ylabel('ice volume (m s.l.e.)', color='0.25')
        tsax.set_xlim(120.0, 0.0)
        tsax.set_ylim(-0.05, 0.35)
        tsax.grid(axis='y')
        tsax.locator_params(axis='y', nbins=6)

    # load aggregated data
    with pismx.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot map data
        glaciated = ds.cumu_erosion > 0.0
        ds.cumu_erosion.where(glaciated).plot.contourf(
            ax=ax, alpha=0.75, cmap='YlOrBr', cbar_ax=cax,
            cbar_kwargs=dict(label='total erosion (m)', format='%g'),
            levels=[10**i for i in range(0, 5)])
        glaciated.plot.contour(ax=ax, colors='k', linewidths=0.5, levels=[0.5])

        # plot time series
        data = ds.erosion_rate*1e-9
        roll = data.rolling(age=100, center=True).mean()
        twax = tsax.twinx()
        twax.plot(data.age, data, c='C11', alpha=0.5)
        twax.plot(data.age, roll, c='C11')
        twax.set_ylabel(r'erosion rate ($km\,a^{-1}$)', color='C11')
        twax.set_xlim(120.0, 0.0)
        twax.set_ylim(-0.5, 3.5)

    # add map elements
    util.geo.draw_boot_topo(ax)
    util.geo.draw_natural_earth(ax)

    # save figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
