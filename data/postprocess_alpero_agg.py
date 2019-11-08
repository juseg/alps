#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPERO aggregated variables."""

import os
import sys
import datetime
import xarray as xr

# processed runs
PROC_RUNS = ['alpcyc4.2km.grip.0820', 'alpcyc4.2km.grip.1040.pp',
             'alpcyc4.2km.epica.0970', 'alpcyc4.2km.epica.1220.pp',
             'alpcyc4.2km.md012444.0800', 'alpcyc4.2km.md012444.1060.pp',
             'alpcyc4.1km.epica.1220.pp']

# global attributes
GLOB_ATTRS = dict(
    title='Alpine ice sheet glacial cycle erosion aggregated variables',
    author='Julien Seguinot',
    institution='ETH Zürich, Switzerland and Hokkaido University, Japan',
    command='{user}@{host} {time}: {cmdl}\n'.format(
        user=os.environ['USER'], host=os.uname()[1], cmdl=' '.join(sys.argv),
        time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')))


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    out_file = 'processed/alpero.{}.{}.{}.agg.nc'.format(
        res, rec[:4], 'pp' if 'pp' in other else 'cp')
    subtitle = '{} {} simulation {} precipitation reductions'.format(
        res, rec.upper(), 'with' if 'pp' in other else 'without')

    # load output data (in the future combine='by_coords' will be the default)
    print("loading " + run_path + "...")
    ex = xr.open_mfdataset(run_path+'/ex.???????.nc', decode_times=False,
                           chunks=dict(time=50), combine='by_coords',
                           data_vars='minimal', master_file=-1)

    # get global attributes from last file (issue #2382, fixed locally)
    # last = xr.open_dataset(run_path+'/ex.0120000.nc', decode_times=False)
    # ex.attrs = last.attrs
    # last.close()

    # create age coordinate and extract time step
    ex['age'] = ex.time/(-365.0*24*60*60)
    ex['age'].attrs['units'] = 'years'
    dt = ex.age[0] - ex.age[1]

    # init postprocessed dataset with global attributes
    pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))
    pp.attrs.update(subtitle=subtitle, **GLOB_ATTRS)
    pp.attrs.update(history=pp.command+pp.history)

    # register intermediate variables (erosion Herman et al., 2015)
    ex['icy'] = (ex.thk >= 1.0)
    ex['erosion'] = 2.7e-7*(ex.icy*ex.velbase_mag)**2.02  # m/a
    ex['warmbase'] = ex.icy*(ex.temppabase >= -1e-3)

    # compute last basal velocity transgressive variables
    # compute index first (xarray indexing with dask array issue #2511)
    # idx = (ex.icy*(ex.velbase_mag >= 1.0))[::-1].argmax(axis=0).compute
    # pp['lastbvage'] = ex.age[-idx].where(idx > 0).assign_attrs(
    #     long_name='last basal velocity age', units=ex.age.units)
    # pp['lastbvbvx'] = ex.uvelbase[-idx].where(idx > 0).assign_attrs(
    #     long_name='last basal velocity x-component', units=ex.uvelbase.units)
    # pp['lastbvbvy'] = ex.vvelbase[-idx].where(idx > 0).assign_attrs(
    #     long_name='last basal velocity y-component', units=ex.vvelbase.units)
    # pp.drop('time')

    # compute glacial cycle integrated variables
    pp['totalslip'] = dt*(ex.icy*ex.velbase_mag).sum(axis=0).assign_attrs(
        long_name='cumulative basal motion', units='m')
    pp['glerosion'] = dt*ex.erosion.sum(axis=0).assign_attrs(
        long_name='cumulative glacial erosion', units='m year-1')
    pp['warmcover'] = dt*ex.warmbase.sum(axis=0).assign_attrs(
        long_name='temperate-based ice cover duration', units='years')

    # copy grid mapping and pism config
    pp['mapping'] = ex.mapping
    pp['pism_config'] = ex.pism_config

    # export to netcdf
    pp.to_netcdf(out_file, mode='w', encoding={var: dict(
        zlib=True, shuffle=True, complevel=5) for var in pp.variables})

    # close datasets
    ex.close()
    pp.close()


def main():
    """Main program called during execution."""

    # create directory if missing
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # postprocess selected runs
    for run in PROC_RUNS:
        postprocess_extra(os.environ['HOME'] + '/pism/output/e9d2d1f/' + run)


if __name__ == '__main__':
    main()
