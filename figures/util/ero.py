# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Alps glacial erosion paper utils.
"""

import hyoga.open
import matplotlib.pyplot as plt


def plot_series(ax=None, run='1km.epic.pp'):
    """Plot ice volume and erosion time series."""

    # get current axes if None provided
    ax = ax or plt.gca()

    # load time series
    with hyoga.open.dataset(
            '../data/processed/alpcyc.'+run+'.ts.10a.nc') as ds:

        # plot ice volume time series
        ax.plot(ds.age, ds.slvol*100, c='0.25')
        ax.set_xlabel('age (ka)')
        ax.set_ylabel('ice volume (cm s.l.e.)', color='0.25')
        ax.set_xlim(120, 0)
        ax.set_ylim(-5, 35)
        ax.locator_params(axis='y', nbins=6)

        # hatch regions of low ice volume
        ax.fill_between(
            ds.age, -10, 40, where=(ds.slvol < 0.03),
            edgecolor='0.75', facecolor='none', hatch='//////')

    # load aggregated data
    with hyoga.open.dataset(
            '../data/processed/alpero.'+run+'.agg.nc') as ds:

        # plot erosion rate time series
        ds['rolling_mean'] = ds.kop2015_rate.rolling(
            age=100, center=True).mean()
        ax = ax.twinx()
        ax.plot(ds.age, ds.kop2015_rate*1e-6, c='C11', alpha=0.5)
        ax.plot(ds.age, ds.rolling_mean*1e-6, c='C11')
        ax.set_ylabel('potential annual erosion\n'
                      r'volume ($10^6\,m^3 a^{-1}$)', color='C11')
        ax.set_ylim(-1, 7)
