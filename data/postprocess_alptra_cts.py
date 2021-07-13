#!/usr/bin/env python
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPTRA time series and spatial diagnostics."""

import os
import sys
import datetime
import hyoga

# processed runs
PROC_RUNS = ['alptra1.1km.epica.1220.pp', 'alptra1.500m.epica.1220.pp']


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    prefix = 'processed/alptra.{}.{}.{}'.format(
        res, rec[:4], 'pp' if 'pp' in other else 'cp')

    # global attributes
    attributes = {
        'author':       'Julien Seguinot',
        'title':        'Alpine ice sheet glacial maximum flow simulations',
        'subtitle':     '{} {} simulation {} precipitation reductions'.format(
            res, rec.upper(), 'with' if 'pp' in other else 'without'),
        'institution':  '',
        'command':      '{user}@{host} {time}: {cmdl}\n'.format(
            user=os.getlogin(), host=os.uname()[1], cmdl=' '.join(sys.argv),
            time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))}

    # postprocess scalar time series
    print("postprocessing " + prefix + "...")
    with hyoga.open.mfdataset(run_path+'/ts.???????.nc') as ts:

        # select age slice
        step = 10 if res == '1km' else 1
        ts = ts.isel(age=slice(step-1, None, step))

        # assign attributes and export compressed file
        ts.attrs.update(history=attributes['command']+ts.history, **attributes)
        ts.attrs.update(title=ts.title + ' scalar time series')
        ts.to_netcdf(prefix + '.ts.1m.nc', encoding={var: dict(
            zlib=True, shuffle=True, complevel=1) for var in ts.variables})

        # find age of max extent
        age = float(ts.ice_area_glacierized.idxmax())
        print("found maximum extent at {:g} ka.".format(age))

    # postprocess spatial diagnostics
    with hyoga.open.subdataset(run_path+'/ex.{:07.0f}.nc', time=-age*1e3,
                               shift=120e3, tolerance=1) as ex:

        # apply ice thickness mask
        print("found nearest slice at {:g} ka.".format(ex.age.values))
        ex = ex.hyoga.where_thicker(1)

        # assign attributes and export compressed file
        ex.attrs.update(history=attributes['command']+ex.history, **attributes)
        ex.attrs.update(title=ex.title + ' spatial diagnostics')
        ex.to_netcdf(prefix + '.ex.lgm.nocomp.nc')
        ex.to_netcdf(prefix + '.ex.lgm.nc', encoding={var: dict(
            zlib=True, shuffle=True, complevel=1) for var in ex.variables})

    # postprocess time stamps (NOTE ex.0095050.nc is broken)
    if '500m' in run_path:
        filename = [os.path.expanduser(run_path+'/ex.0095{:03d}.nc'.format(t))
                    for t in range(20, 500, 10)]
    else:
        filename = run_path + '/ex.???????.nc'
    with hyoga.open.mfdataset(
            filename, coords='minimal', compat='override') as ex:

        # assign attributes and export compressed file
        ts = ex[['timestamp']]
        ts.attrs.update(history=attributes['command']+ex.history, **attributes)
        ts.attrs.update(title=ts.title + ' time stamps')
        ts.to_netcdf(prefix + '.tms.nc', encoding={var: dict(
            zlib=True, shuffle=True, complevel=1) for var in ts.variables})


def main():
    """Main program called during execution."""

    # create directory if missing
    os.makedirs('processed', exist_ok=True)

    # postprocess selected runs
    for run in PROC_RUNS:
        postprocess_extra('~/pism/output/1.1.3/' + run)


if __name__ == '__main__':
    main()
