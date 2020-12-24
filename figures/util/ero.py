# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Alps glacial erosion paper utils.
"""

import pismx.open
import matplotlib.pyplot as plt


def plot_series(ax=None, run='1km.epic.pp'):
    """Plot ice volume and erosion time series."""

    # get current axes if None provided
    ax = ax or plt.gca()

    # load time series
    with pismx.open.dataset(
            '../data/processed/alpcyc.'+run+'.ts.10a.nc') as ds:

        # plot ice volume time series
        ax.plot(ds.age, ds.slvol*100, c='0.25')
        ax.set_xlabel('age (ka)')
        ax.set_ylabel('ice volume (cm s.l.e.)', color='0.25')
        ax.set_xlim(120, 0)
        ax.set_ylim(-5, 35)
        ax.locator_params(axis='y', nbins=6)

    # load aggregated data
    with pismx.open.dataset(
            '../data/processed/alpero.'+run+'.agg.nc') as ds:

        # plot erosion rate time series
        ds['rolling_mean'] = ds.her2015_rate.rolling(age=100, center=True).mean()
        ax = ax.twinx()
        ax.plot(ds.age, ds.her2015_rate*1e-9, c='C11', alpha=0.5)
        ax.plot(ds.age, ds.rolling_mean*1e-9, c='C11')
        ax.set_ylabel(r'erosion rate ($km^3\,a^{-1}$)', color='C11')
        ax.set_ylim(-0.5, 3.5)
