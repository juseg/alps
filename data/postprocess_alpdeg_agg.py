#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPERO aggregated variables."""

import os
import sys
import datetime
import xarray as xr
import pismx.open

# processed runs
PROC_RUNS = ['alpcyc4.2km.grip.0820', 'alpcyc4.2km.grip.1040.pp',
             'alpcyc4.2km.epica.0970', 'alpcyc4.2km.epica.1220.pp',
             'alpcyc4.2km.md012444.0800', 'alpcyc4.2km.md012444.1060.pp',
             'alpcyc4.1km.epica.1220.pp']

# global attributes
GLOB_ATTRS = dict(
    title='Alpine ice sheet deglaciation aggregated variables',
    author='Julien Seguinot',
    institution='ETH Zürich, Switzerland',
    command='{user}@{host} {time}: {cmdl}\n'.format(
        user=os.getlogin(), host=os.uname()[1], cmdl=' '.join(sys.argv),
        time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')),
    comment="""Aggregated dataset contents:
* Spatial variables aggregated in time corresponding to the last model output
before final deglaciation.
""")


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    out_file = 'processed/alpdeg.{}.{}.{}.agg.nc'.format(
        res, rec[:4], 'pp' if 'pp' in other else 'cp')

    # load output data (in the future combine='by_coords' will be the default)
    print("postprocessing " + out_file + "...")
    boot = pismx.open.dataset(
        '~/pism/input/boot/'+'alps.srtm.hus12.gou11simi.{}.nc'.format(res))
    ex = pismx.open.mfdataset(run_path+'/ex.???????.nc')

    # init postprocessed dataset with global attributes
    pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))
    pp.attrs.update(
        subtitle='{} {} simulation {} precipitation reductions'.format(
            res, rec.upper(), 'with' if 'pp' in other else 'without'),
        **GLOB_ATTRS)
    pp.attrs.update(history=pp.command+pp.history)

    # compute grid size
    dt = ex.age[0] - ex.age[1]
    dt = dt*1e3  # convert ka to a

    # compute last ice cover transgressive variables
    idx = (ex.thk >= 1)[::-1].argmax(axis=0).compute()
    pp['deglacage'] = (ex.age[-idx].where(idx > 0)).assign_attrs(
        long_name='last ice cover age', units=ex.age.units)

    # compute last basal velocity transgressive variables
    # compute index first (xarray indexing with dask array issue #2511)
    idx = ((ex.thk >= 1)*(ex.velbase_mag >= 1))[::-1].argmax(axis=0).compute()
    pp['lastslipa'] = ex.age[-idx].where(idx > 0).assign_attrs(
        long_name='last basal velocity age', units=ex.age.units)
    pp['lastslipu'] = ex.uvelbase[-idx].where(idx > 0).assign_attrs(
        long_name='last basal velocity x-component', units=ex.uvelbase.units)
    pp['lastslipv'] = ex.vvelbase[-idx].where(idx > 0).assign_attrs(
        long_name='last basal velocity y-component', units=ex.vvelbase.units)
    pp.drop('time')

    # export to netcdf
    pp.to_netcdf(out_file, mode='w', encoding={var: dict(
        zlib=True, shuffle=True, complevel=1) for var in pp.variables})

    # close datasets
    boot.close()
    ex.close()
    pp.close()


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


if __name__ == '__main__':
    main()
