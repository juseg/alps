#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPERO aggregated variables."""

import os
import sys
import datetime
import numpy as np
import xarray as xr
import pismx.open

# processed runs
PROC_RUNS = ['alpcyc4.2km.grip.0820', 'alpcyc4.2km.grip.1040.pp',
             'alpcyc4.2km.epica.0970', 'alpcyc4.2km.epica.1220.pp',
             'alpcyc4.2km.md012444.0800', 'alpcyc4.2km.md012444.1060.pp',
             'alpcyc4.1km.epica.1220.pp']

# global attributes
GLOB_ATTRS = dict(
    title='Alpine ice sheet glacial cycle erosion aggregated variables',
    author='Julien Seguinot',
    institution='ETH Zürich, Switzerland',
    command='{user}@{host} {time}: {cmdl}\n'.format(
        user=os.getlogin(), host=os.uname()[1], cmdl=' '.join(sys.argv),
        time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')),
    comment="""Aggregated dataset contents:
* Spatial variables aggregated in time over the entire simulation lenght from
120,000 years before present to the present (cumu_erosion, cumu_sliding,
glacier_time, warmbed_time).
* Time-series variables aggregated in space over the entire glaciated area,
defined by a 1-metre ice thickness threshold (erosion_rate, glacier_area,
warmbed_area).
""")


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    boot_file = (os.environ['HOME'] + '/pism/input/boot/' +
                 'alps.srtm.hus12.gou11simi.{}.nc'.format(res))
    out_file = 'processed/alpero.{}.{}.{}.agg.nc'.format(
        res, rec[:4], 'pp' if 'pp' in other else 'cp')
    subtitle = '{} {} simulation {} precipitation reductions'.format(
        res, rec.upper(), 'with' if 'pp' in other else 'without')

    # load output data (in the future combine='by_coords' will be the default)
    print("postprocessing " + out_file + "...")
    boot = pismx.open.dataset(boot_file)
    ex = pismx.open.mfdataset(run_path+'/ex.???????.nc')

    # init postprocessed dataset with global attributes
    pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))
    pp.attrs.update(subtitle=subtitle, **GLOB_ATTRS)
    pp.attrs.update(history=pp.command+pp.history)

    # register intermediate variables
    ex['icy'] = (ex.thk >= 1.0)
    ex['bedlift'] = ex.topg - boot.topg.where(boot.topg > 0, 0)
    ex['sliding'] = ex.icy*ex.velbase_mag
    ex['erosion'] = 2.7e-7*ex.sliding**2.02  # (m/a, Herman et al., 2015)
    ex['warmbed'] = ex.icy*(ex.temppabase >= -1e-3)

    # compute grid size
    dt = ex.age[0] - ex.age[1]
    dx = ex.x[1] - ex.x[0]
    dy = ex.y[1] - ex.y[0]

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
    pp['cumu_erosion'] = (dt*ex.erosion.sum(axis=0)).assign_attrs(
        long_name='cumulative glacial erosion', units='m')
    pp['cumu_sliding'] = (dt*ex.sliding.sum(axis=0)).assign_attrs(
        long_name='cumulative basal motion', units='m')
    pp['glacier_time'] = (dt*ex.icy.sum(axis=0)).assign_attrs(
        long_name='temperate-based ice cover duration', units='years')
    pp['warmbed_time'] = (dt*ex.warmbed.sum(axis=0)).assign_attrs(
        long_name='temperate-based ice cover duration', units='years')

    # compute timeseries
    pp['erosion_rate'] = (dx*dy*ex.erosion.sum(axis=(1, 2))).assign_attrs(
        long_name='volumic glacial erosion rate', units='m3 year-1')
    pp['glacier_area'] = (dx*dy*ex.icy.sum(axis=(1, 2))).assign_attrs(
        long_name='glacierized area', units='m2')
    pp['volumic_lift'] = (dx*dy*ex.bedlift.sum(axis=(1, 2))).assign_attrs(
        long_name='volumic bedrock uplift', units='m3')
    pp['warmbed_area'] = (dx*dy*ex.warmbed.sum(axis=(1, 2))).assign_attrs(
        long_name='temperate-based ice cover area', units='m2')

    # compute hypsogram
    pp['erosion_hyps'] = np.exp(
        np.log(ex.erosion.where(ex.erosion > 0)).groupby_bins(
            boot.topg, bins=range(0, 4501, 100), precision=1).mean(
            dim='stacked_y_x')).assign_attrs(
        long_name='erosion rate geometric mean', units='m year-1')

    # replace intervals (xarray issue #2847)
    pp['topg_bins'] = [b.mid for b in pp.topg_bins.values]
    pp = pp.rename({'topg_bins': 'z'})

    # copy grid mapping and pism config
    pp['mapping'] = ex.mapping
    pp['pism_config'] = ex.pism_config

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
