#!/usr/bin/env python
# Copyright (c) 2019-2023, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPCYC continuous variables."""

import os
import sys
import datetime
import hyoga.open

# processed runs
PROC_RUNS = ['alpcyc4.2km.grip.0820', 'alpcyc4.2km.grip.1040.pp',
             'alpcyc4.2km.epica.0970', 'alpcyc4.2km.epica.1220.pp',
             'alpcyc4.2km.md012444.0800', 'alpcyc4.2km.md012444.1060.pp',
             'alpcyc4.1km.epica.1220.pp']


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # variables to mask and not
    masked_vars = ['tempicethk_basal', 'temppabase', 'thk',
                   'uvelbase', 'uvelsurf', 'vvelbase', 'vvelsurf']
    nomask_vars = ['x', 'y', 'age', 'lon', 'lat', 'mapping',
                   'pism_config', 'topg']

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    prefix = 'processed/alpcyc.{}.{}.{}'.format(
        res, rec[:4], 'pp' if 'pp' in other else 'cp')

    # global attributes
    attributes = {
        'author':       'Julien Seguinot',
        'title':        'Alpine ice sheet glacial cycle simulations',
        'subtitle':     '{} {} simulation {} precipitation reductions'.format(
            res, rec.upper(), 'with' if 'pp' in other else 'without'),
        'institution':  'ETH Zürich, Switzerland and '
                        'Hokkaido University, Japan',
        'command':      '{user}@{host} {time}: {cmdl}\n'.format(
            user=os.getlogin(), host=os.uname()[1], cmdl=' '.join(sys.argv),
            time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))}

    # postprocess spatial diagnostics and time stamps
    print("postprocessing " + prefix + "...")
    with hyoga.open.mfdataset(run_path+'/ex.???????.nc') as ex:

        # select extra variables and ages
        step = 100 if res == '1km' else 10
        ts = ex[['timestamp']]
        ex = ex[masked_vars+nomask_vars].isel(age=slice(step-1, None, step))

        # apply mask where needed
        for var in masked_vars:
            ex[var] = ex[var].where(ex.thk.fillna(0) >= 1)

        # assign attributes and export compressed file
        ex.attrs.update(history=attributes['command']+ex.history, **attributes)
        ex.attrs.update(title=ex.title + ' spatial diagnostics')
        ex.to_netcdf(prefix + '.ex.1ka.nc', encoding={var: dict(
            zlib=True, shuffle=True, complevel=1) for var in ex.variables})

        # assign attributes and export compressed file
        ts.attrs.update(history=attributes['command']+ex.history, **attributes)
        ts.attrs.update(title=ex.title + ' time stamps')
        ts.to_netcdf(prefix + '.tms.nc', encoding={var: dict(
            zlib=True, shuffle=True, complevel=1) for var in ts.variables})

    # postprocess scalar time series
    with hyoga.open.mfdataset(run_path+'/ts.???????.nc') as ts:

        # select age slice
        step = 10 if res == '1km' else 1
        ts = ts.isel(age=slice(step-1, None, step))

        # assign attributes and export compressed file
        ts.attrs.update(history=attributes['command']+ts.history, **attributes)
        ts.attrs.update(title=ex.title + ' scalar time series')
        ts.to_netcdf(prefix + '.ts.10a.nc', encoding={var: dict(
            zlib=True, shuffle=True, complevel=1) for var in ts.variables})


def main():
    """Main program called during execution."""

    # create directory if missing
    os.makedirs('processed', exist_ok=True)

    # postprocess selected runs
    for run in PROC_RUNS:
        postprocess_extra('~/pism/output/e9d2d1f/' + run)


if __name__ == '__main__':
    main()
