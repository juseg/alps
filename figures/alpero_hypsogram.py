#!/usr/bin/env python
# Copyright (c) 2019-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion hypsogram."""

import os
import numpy as np
import xarray as xr
import matplotlib.colors as mcolors
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax, tsax) = apl.subplots_mm(
        figsize=(177, 119), nrows=2, sharex=True, gridspec_kw=dict(
            left=1.5+10, right=1.5+18, bottom=1.5+8, top=1.5,
            hspace=4, height_ratios=(3, 1)))
    cax = fig.add_axes_mm([177-1.5-16, 1.5+38, 4, 78])

    # load aggregated data
    with pismx.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot hypsogram
        np.log10(ds.her2015_hyps).plot.imshow(
            ax=ax, x='age', cmap='YlOrBr', vmin=-10, vmax=0, cbar_ax=cax,
            cbar_kwargs=dict(label=r'log10 erosion rate ($m\,a^{-1}$)'))
        # this should work in matplotlib 3.3.2 (PR #18458)
        # ds.her2015_hyps.plot.imshow(
        #    ax=ax, x='age', cmap='YlOrBr', norm=mcolors.LogNorm(1e-9, 1e0),
        #    cbar_ax=cax, cbar_kwargs=dict(label=r'erosion rate ($m\,a^{-1}$)'))
        ax.set_xlabel('')
        ax.set_ylabel('elevation (m)')

    # plot time series
    util.fig.plot_mis(ax, y=None)
    util.fig.plot_mis(tsax, y=1.075)
    util.ero.plot_series(ax=tsax)

    # save figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
