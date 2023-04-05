#!/usr/bin/env python
# Copyright (c) 2018-2023, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Check ALPCYC aggregated variables against previous version."""

import os
import glob
import urllib.request
import hyoga.open


def main():
    """Main program called during execution."""

    # changed to processed directory
    os.chdir('processed')

    # for each availabe file
    for newfile in sorted(glob.glob('alpcyc.2km.????.??.??.??a.nc')):

        # download corresponding online file
        oldfile = newfile[:-3] + '.old.nc'
        if not os.path.isfile(oldfile):
            urllib.request.urlretrieve(
                'https://zenodo.org/record/1423176/files/' + newfile, oldfile)

        # open old and new datasets
        with hyoga.open.dataset(newfile, chunks=None) as new, \
                hyoga.open.dataset(oldfile, chunks=None) as old:

            # compute the difference
            diff = (new - old).compute()
            print(newfile + ' mean differences:', abs(diff).mean())
            diff.to_netcdf(newfile[:-3] + '.diff.nc')


if __name__ == '__main__':
    main()
