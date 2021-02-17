#!/usr/bin/env python
# Copyright (c) 2016-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion final basal sliding."""

import matplotlib.colors as mcolors
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax, cax = util.fig.subplots_cax(extent='rhlobe')

    # load aggregated data
    with pismx.open.mfdataset(
            '../data/processed/alpdeg.1km.epic.pp.agg.nc') as ds:

        # plot map data
        plot = ax.streamplot(
            ds.x, ds.y, ds.lastslipu.values, ds.lastslipv.values,
            color=ds.lastslipa.values, cmap='Spectral',
            norm=mcolors.Normalize(vmin=15, vmax=25),
            density=(12, 8), linewidth=0.5, arrowsize=0.25)
        ds.deglacage.notnull().plot.contourf(
            ax=ax, add_colorbar=False, extend='neither', alpha=0.75,
            colors='w', levels=[0.5, 1.5])
        (ds.deglacage.notnull() ^ ds.lastslipa.notnull()).plot.contourf(
            ax=ax, add_colorbar=False, colors='none', extend='neither',
            hatches=['////'], levels=[0.5, 1.5])
        ds.deglacage.notnull().plot.contour(
            ax=ax, colors='0.25', levels=[0.5], linewidths=0.5)
        ds.lastslipa.notnull().plot.contour(
            ax=ax, colors='0.25', levels=[0.5], linewidths=0.5,
            linestyles='dashed')

    # add map elements
    util.geo.draw_boot_topo(ax)
    util.geo.draw_natural_earth(ax)

    # add colorbar
    fig.colorbar(plot.lines, cax, extend='both').set_label(
        r'age of last basal sliding (ka)')

    # save figure
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
