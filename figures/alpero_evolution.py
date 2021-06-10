#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion time evolution."""

import os
import absplots as apl
import hyoga.open
import util  # noqa color cycle


def main():
    """Main program called during execution."""

    # erosion law
    law = os.getenv('ALPERO_LAW', 'kop2015')

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(85, 80), gridspec_kw=dict(
        left=12, right=1.5, bottom=9, top=1.5))

    # load postprocessed data (note: there seem to be currently no way to merge
    # two dataset with slight errors using mfdataset)
    with hyoga.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
        with hyoga.open.dataset(
                '../data/processed/alpero.1km.epic.pp.agg.nc') as agg:
            agg = agg.reindex_like(ds, method='nearest', tolerance=1e-9)
            ds = ds.merge(agg, compat='override')

    # unit conversion and rolling mean
    ds['slvol'] *= 100
    erosion = ds[law+'_rate']
    rolling = erosion.rolling(age=100, center=True).mean()
    ds['growing'] = ds.slvol.differentiate('age') < 0  # age coord decreasing

    # plot
    ax.plot(ds.slvol, erosion.where(ds.growing), c='C1', alpha=0.25)
    ax.plot(ds.slvol, erosion.where(~ds.growing), c='C11', alpha=0.25)
    ax.plot(ds.slvol, rolling.where(ds.growing), c='C1', ls='--')
    ax.plot(ds.slvol, rolling.where(~ds.growing), c='C11')
    ax.text(0.95, 0.95, '', ha='right', va='top', transform=ax.transAxes)

    # hatch regions of low ice volume
    ax.fill_between(
        [-3, 3], 1e4, 1e11, edgecolor='0.75', facecolor='none', hatch='//////')

    # set axes properties
    ymid = erosion.where(ds.slvol > 3).mean()
    ax.set_xlabel('ice volume (cm s.l.e.)')
    ax.set_ylabel(r'potential annual erosion volume ($m^3 a^{-1}$)')
    ax.set_yscale('log')
    ax.set_xlim(-1.5, 31.5)
    ax.set_ylim(ymid/50, ymid*50)

    # annotate advance and retreat
    ax.annotate('', xy=(0.2, 0.7), xytext=(0.8, 0.7), arrowprops=dict(
        arrowstyle='->', color='C11', lw=1, connectionstyle='arc3,rad=0.25'),
                textcoords='axes fraction', xycoords='axes fraction')
    ax.annotate('', xy=(0.8, 0.25), xytext=(0.2, 0.25), arrowprops=dict(
        arrowstyle='->', color='C1', lw=1, connectionstyle='arc3,rad=0.25'),
                textcoords='axes fraction', xycoords='axes fraction')
    ax.text(0.5, 0.1, 'advance', color='C1', ha='center', va='center',
            transform=ax.transAxes)
    ax.text(0.5, 0.85, 'retreat', color='C11', ha='center', va='center',
            transform=ax.transAxes)

    # annotate maximum stages
    ymis4 = rolling.sel(age=65.7)
    ymis2 = rolling.sel(age=24.5)
    ax.plot(21, ymis4, marker='o', ms=40, mec='0.25', mfc='none')
    ax.plot(28, ymis2, marker='o', ms=40, mec='0.25', mfc='none')
    ax.text(21, ymis4*(10**0.5), 'MIS 4', ha='center', va='center')
    ax.text(28, ymis2*(10**0.5), 'MIS 2', ha='center', va='center')

    # save
    fig.savefig(__file__[:-3] + ('_'+law if law != 'kop2015' else ''))


if __name__ == '__main__':
    main()
