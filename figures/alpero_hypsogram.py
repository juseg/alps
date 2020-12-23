#!/usr/bin/env python
# Copyright (c) 2019-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion hypsogram."""

import numpy as np
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax, tsax) = apl.subplots_mm(
        figsize=(177, 80), nrows=2, sharex=True, gridspec_kw=dict(
            left=12, right=18, bottom=9, top=1.5,
            hspace=1.5, height_ratios=(48, 20)))
    cax = fig.add_axes_mm([177-16.5, 9+20+1.5, 3, 48])

    # load aggregated data
    with pismx.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot hypsogram
        np.log10(ds.her2015_hyps).plot.imshow(
            ax=ax, alpha=0.75, cmap='YlOrBr', vmin=-9, vmax=0, x='age',
            cbar_ax=cax, cbar_kwargs=dict(
                label=r'log10 erosion rate ($m\,a^{-1}$)'))
        # this should work in matplotlib 3.3.2 (PR #18458)
        # ds.her2015_hyps.plot.imshow(
        #    ax=ax, alpha=0.75, cmap='YlOrBr', norm=mcolors.LogNorm(1e-9, 1e0),
        #    x='age', cbar_ax=cax, cbar_kwargs=dict(
        #        label=r'erosion rate ($m\,a^{-1}$)'))
        ax.set_xlabel('')
        ax.set_ylabel('elevation (m)')

    # plot time series
    util.fig.plot_mis(ax=tsax, y=0.9)
    util.ero.plot_series(ax=tsax)

    # save figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
