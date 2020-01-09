#!/usr/bin/env python
# Copyright (c) 2018-2020, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Check ALPCYC aggregated variables against previous version."""

import os
import glob
import urllib.request
import xarray as xr


def main():
    """Main program called during execution."""

    # changed to processed directory
    os.chdir('processed')

    # for each availabe file
    for newfile in glob.glob('alpcyc.?km.????.??.agg.nc'):

        # download corresponding online file
        oldfile = newfile[:-3] + '.old.nc'
        if not os.path.isfile(oldfile):
            urllib.request.urlretrieve(
                'https://zenodo.org/record/1423160/files/' + newfile, oldfile)

        # open old and new datasets
        with xr.open_dataset(newfile) as new, xr.open_dataset(oldfile) as old:

            # convert ages to ka
            for var in old:
                if (var == 'covertime' and 'units' not in old[var].attrs) or \
                   (var.endswith('age') and old[var].units == 'years'):
                    old[var] /= 1e3

            # compute the difference
            diff = new.astype(float) - old.astype(float)
            print(newfile + ' mean differences:', abs(diff).mean())
            diff.to_netcdf(newfile[:-3] + '.diff.nc')


if __name__ == '__main__':
    main()
