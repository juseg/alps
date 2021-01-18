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
    fig = apl.figure_mm(figsize=(177, 80))
    spec = fig.add_gridspec_mm(
        ncols=2, nrows=2, left=12, right=1.5, bottom=9, top=1.5, hspace=1.5,
        wspace=1.5, height_ratios=(48, 20), width_ratios=(142, 20))
    ax = fig.add_subplot(spec[0, 0])
    hax = fig.add_subplot(spec[0, 1], sharey=ax)
    tsax = fig.add_subplot(spec[1, 0], sharex=ax)
    cax = fig.add_axes_mm([177-18+1.5, 9+20+1.5+24, 3, 24])

    # add subfigure labels
    util.fig.add_subfig_label('(a)', ax=ax)
    util.fig.add_subfig_label('(b)', ax=tsax)

    # load aggregated data
    with pismx.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # plot hypsogram
        (np.log10(ds.kop2015_hyps)+3).plot.imshow(
            ax=ax, alpha=0.75, cmap='YlOrBr', vmin=-9, vmax=0, x='age',
            cbar_ax=cax, cbar_kwargs=dict(
                label='log10 geometric mean\n'+r'erosion rate ($mm\,a^{-1}$)',
                ticks=range(-9, 1, 3)))
        # this should work in matplotlib 3.3.2 (PR #18458)
        # (ds.kop2015_hyps*1e3).plot.imshow(
        #    ax=ax, alpha=0.75, cmap='YlOrBr', norm=mcolors.LogNorm(1e-9, 1e0),
        #    x='age', cbar_ax=cax, cbar_kwargs=dict(
        #        label=r'erosion rate ($m\,a^{-1}$)'))
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_ylabel('elevation (m)')
        ax.tick_params(labelbottom=False)

    # plot boot hypsometry
    with pismx.open.dataset('../data/processed/alpcyc.1km.in.nc') as ds:

        # plot boot hypsometry
        bins = np.arange(0, 4501, 100)
        hist, _ = np.histogram(ds.topg.where(ds.topg > 0), bins=bins)
        vals = np.append(hist, hist[-1])  # needed to fill the last bin
        hax.fill_betweenx(bins, 0*vals, vals, color='0.25', step='post')
        hax.grid(False)
        hax.set_frame_on(False)
        hax.set_xlim(0, 60000)
        hax.set_xticks([])
        hax.tick_params(labelleft=False)

    # plot time series
    util.fig.plot_mis(ax=ax, y=None)
    util.fig.plot_mis(ax=tsax, y=0.9)
    util.ero.plot_series(ax=tsax)
    tsax.set_ylabel('ice volume\n(cm s.l.e.)')

    # save figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
