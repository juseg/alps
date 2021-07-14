#!/usr/bin/env python
# Copyright (c) 2018-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps transfluences timeseries."""

import brokenaxes as bax
import absplots as apl
import hyoga
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(177, 85))
    spec = fig.add_gridspec_mm(
        ncols=1, nrows=2, left=15, right=1.5, bottom=15, top=1.5, hspace=1.5)
    axes = [bax.brokenaxes(
        despine=False, width_ratios=[2, 1], wspace=0.02, subplot_spec=subspec,
        tilt=75, xlims=((120, 25.5), (25.5, 24))) for subspec in spec]

    # and subfig labels
    for ax, label in zip(axes, 'ab'):
        util.fig.add_subfig_label('(%s)' % label, ax=ax.axs[0])

    # plot alpcyc 1km variables
    with hyoga.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
        axes[0].plot(
            ds.age, ds.area_glacierized*1e-9, c='0.25', label='1km')
        axes[1].plot(
            ds.age, ds.volume_glacierized/ds.area_glacierized, c='0.25')

    # plot alpflo 500m ice volume
    with hyoga.open.dataset(
            '../data/processed/alptra.500m.epic.pp.ts.1m.nc') as ds:
        axes[0].plot(
            ds.age, ds.ice_area_glacierized*1e-9, c='C1', label='500m')
        axes[1].plot(
            ds.age, ds.ice_volume_glacierized/ds.ice_area_glacierized, c='C1')

        # highlight max extent
        age = ds.ice_area_glacierized.idxmax()
        axes[0].axvline(age, color='C1', linewidth=0.5)

    # set axes properties
    axes[0].set_xticklabels([])
    axes[0].set_ylabel(r'ice area ($10^3 km^2$)')
    axes[1].set_ylabel('mean thickness (m)')
    axes[1].set_xlabel('model age (ka)')
    axes[1].legend(loc='lower right')
    axes[1].axs[1].set_xticks([25.5, 25, 24.5, 24])

    # save figure
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
