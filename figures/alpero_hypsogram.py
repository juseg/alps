#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion hypsogram."""

import numpy as np
import matplotlib.pyplot as plt
import absplots as apl
import xarray as xr
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(177, 80))
    spec = fig.add_gridspec_mm(
        ncols=2, nrows=2, left=15, right=1.5, bottom=9, top=1.5, hspace=1.5,
        wspace=1.5, height_ratios=(48, 20), width_ratios=(132, 30))
    ax = fig.add_subplot(spec[0, 0])
    hax = fig.add_subplot(spec[0, 1], sharey=ax)
    tsax = fig.add_subplot(spec[1, 0], sharex=ax)
    cax = fig.add_axes_mm([177-21+1.5, 6, 3, 20])

    # add subfigure labels
    util.fig.add_subfig_label('(a)', ax=ax)
    util.fig.add_subfig_label('(b)', ax=tsax)

    # load boot topo
    with xr.open_dataset('../data/processed/alpcyc.1km.in.nc') as ds:
        boot = ds.topg

    # load glaciated footprint
    with xr.open_dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
        glaciated = ds.covertime > 0

    # load aggregated data
    with xr.open_mfdataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as ds:

        # maybe the only way to set hatch color
        plt.rc('hatch', color='0.25')

        # plot hypsogram
        (np.log10(ds.kop2015_hyps)+3).plot.imshow(
            ax=ax, alpha=0.75, cmap='YlOrBr', vmin=-9, vmax=0, x='age',
            cbar_ax=cax, cbar_kwargs=dict(
                label='geometric mean\n'+r'erosion rate ($mm\,a^{-1}$)',
                ticks=range(-9, 1, 3)))
        ds.glacier_hyps.plot.contourf(
            ax=ax, add_colorbar=False, colors='none', extend='neither',
            hatches=['//////'], levels=[0.5e6, 99.5e6], x='age')
        ds.glacier_hyps.plot.contour(
            ax=ax, colors='0.25', levels=[99.5e6], x='age')
        cax.yaxis.set_major_formatter(r'$10^{{{x:d}}}$')
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
        bins = np.arange(0, 4501, 100)
        hax.hist(boot.where(boot > 0).values.ravel(), bins=bins,
                 orientation='horizontal', color='0.75')

        # plot glaciated hypsometry
        hax.hist(boot.where(glaciated).values.ravel(), bins=bins,
                 orientation='horizontal', color='C1')

        # set histogram axes properties
        hax.set_xticks([])
        hax.tick_params(labelleft=False)

        # plot band cumulative erosion in km3
        hax = hax.twiny()
        (ds.kop2015_cumu.groupby_bins(boot, bins).sum()/1e3).plot.step(
            ax=hax, y='topg_bins', color='C11')

        # set twin axes properties
        hax.tick_params(axis='x', direction='in', pad=-15)
        hax.set_xlabel('cumulative erosion\n'+r'volume (km³)',
                       color='C11', labelpad=-30)

    # plot time series
    util.fig.plot_mis(ax=ax, y=None)
    util.fig.plot_mis(ax=tsax, y=0.9)
    util.ero.plot_series(ax=tsax)
    tsax.set_ylabel('ice volume\n(cm s.l.e.)')

    # save figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
