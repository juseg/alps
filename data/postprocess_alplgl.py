#!/usr/bin/env python
# Copyright (c) 2016-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPLGL glaciation threshold map."""

import os
import xarray as xr


def main():
    """Main program called during execution."""

    # create directory if missing
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # compute stacked extent
    stack = -5
    for offset in enumerate(range(-4, 1)):
        with xr.open_dataset(os.path.expanduser(
                '~/pism/output/0.7.3/alplgl1.200m.r100a.{:04d}/ex.0002000.nc'
                .format(-100*offset))) as ex:
            stack = xr.where(ex.thk[-1] > 1.0, offset, stack)

    # export aggregated array
    stack.to_netcdf('processed/alplgl1.200m.r100a.tempdiff.nc')


if __name__ == '__main__':
    main()
