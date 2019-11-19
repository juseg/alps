#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion time evolution."""

import xarray as xr
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(177, 119), gridspec_kw=dict(
        left=12, right=1.5, bottom=12, top=1.5))

    # load postprocessed data
    with xr.open_mfdataset([
            '../data/processed/alpero.1km.epic.pp.agg.nc',
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc'],
                           combine='by_coords', join='override') as ds:
        eros = ds.erosion_rate*1e-9
        roll = eros.rolling(time=100, center=True).mean()
        slvol = ds.slvol*100

    # for volume changes use
    # slvol = slvol.rolling(time=100, center=True).mean()
    # slvol = slvol.differentiate('time')

    # plot
    ax.plot(slvol, eros, c='C11', alpha=0.5)
    ax.plot(slvol, roll, c='C11')

    # set axes properties
    ax.set_xlabel('ice volume (cm s.l.e.)')
    ax.set_ylabel(r'erosion rate ($km^3\,a^{-1}$)')
    ax.set_yscale('log')
    ax.set_ylim(0.8e-2, 1.2e1)

    # save figure
    util.pl.savefig(fig)


if __name__ == '__main__':
    main()
