#!/usr/bin/env python2

import glob
import numpy as np
import xarray as xr

filenames = glob.glob('processed/alpcyc.?km.????.??.agg.nc')

for filename in filenames:
    try:
        with xr.open_dataset(filename) as new:
            with xr.open_dataset(filename.replace('/', '/bkp/')) as old:
                for var in old:
                    if var == 'time':
                        continue
                    elif var =='footprint':
                        diff = (new[var] ^ old[var]).sum().data
                    else:
                        diff = (new[var].data - old[var]).sum().data
                    print var, diff.sum()
    except IOError:
        continue
