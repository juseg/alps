#!/usr/bin/env python
# Copyright (c) 2019--2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPERO continuous variables."""

import os
import sys
import datetime
import xarray as xr

# processed runs
PROC_RUNS = ['alpcyc4.2km.grip.0820', 'alpcyc4.2km.grip.1040.pp',
             'alpcyc4.2km.epica.0970', 'alpcyc4.2km.epica.1220.pp',
             'alpcyc4.2km.md012444.0800', 'alpcyc4.2km.md012444.1060.pp',
             'alpcyc4.1km.epica.1220.pp']
PROC_RUNS = [PROC_RUNS[-1]]

# global attributes
GLOB_ATTRS = dict(
    title='Alpine ice sheet glacial cycle erosion continuous variables',
    author='Julien Seguinot',
    institution='ETH Zürich, Switzerland',
    command='{user}@{host} {time}: {cmdl}\n'.format(
        user=os.environ['USER'], host=os.uname()[1], cmdl=' '.join(sys.argv),
        time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')))


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    out_file = 'processed/alpero.{}.{}.{}.cts.nc'.format(
        res, rec[:4], 'pp' if 'pp' in other else 'cp')
    subtitle = '{} {} simulation {} precipitation reductions'.format(
        res, rec.upper(), 'with' if 'pp' in other else 'without')

    # load output data (in the future combine='by_coords' will be the default)
    print("postprocessing " + out_file + "...")
    ex = xr.open_mfdataset(run_path+'/ex.???????.nc', decode_times=False,
                           chunks=dict(time=50), combine='by_coords',
                           data_vars='minimal', attrs_file=-1)

    # get global attributes from last file (issue #2382, fixed locally)
    # last = xr.open_dataset(run_path+'/ex.0120000.nc', decode_times=False)
    # ex.attrs = last.attrs
    # last.close()

    # add new coordinates
    ex = ex.assign_coords(time=ex.time/(-365.0*24*60*60))
    ex = ex.assign_coords(age=-ex.time)

    # register new variables
    ex['sliding'] = ex.velbase_mag.where(ex.thk >= 1.0)
    ex['erosion'] = (2.7e-7*ex.sliding**2.02).assign_attrs(
        long_name='volumic glacial erosion rate', units='m year-1')

    # select variables to export and update global attributes
    pp = ex[['erosion']].sel(time=ex.time[9::10])
    pp.attrs.update(subtitle=subtitle, **GLOB_ATTRS)
    pp.attrs.update(history=pp.command+pp.history)

    # export to netcdf
    pp.to_netcdf(out_file, mode='w', encoding={var: dict(
        zlib=True, shuffle=True, complevel=1) for var in pp.variables})


def main():
    """Main program called during execution."""

    # create directory if missing
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # activate dask client http://localhost:8787/status
    # from dask.distributed import Client
    # print(Client().scheduler_info()['services'])

    # postprocess selected runs
    for run in PROC_RUNS:
        postprocess_extra(os.environ['HOME'] + '/pism/output/e9d2d1f/' + run)
        break


if __name__ == '__main__':
    main()
