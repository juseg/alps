#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPERO aggregated variables."""

import os
import sys
import datetime
import numpy as np
import xarray as xr
import dask
import dask.diagnostics
import cartowik.profiletools as cpf
import hyoga.open

# processed runs
PROC_RUNS = ['alpcyc4.2km.grip.0820', 'alpcyc4.2km.grip.1040.pp',
             'alpcyc4.2km.epica.0970', 'alpcyc4.2km.epica.1220.pp',
             'alpcyc4.2km.md012444.0800', 'alpcyc4.2km.md012444.1060.pp',
             'alpcyc4.1km.epica.1220.pp']

# global attributes
GLOB_ATTRS = dict(
    title='Alpine ice sheet glacial cycle erosion aggregated variables',
    author='Julien Seguinot',
    institution='',
    command='{user}@{host} {time}: {cmdl}\n'.format(
        user=os.getlogin(), host=os.uname()[1], cmdl=' '.join(sys.argv),
        time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')),
    comment="""Aggregated dataset contents:
* Spatial variables aggregated in time over the entire simulation lenght from
120,000 years before present to the present.
* Time-series variables aggregated in space over the entire glaciated area,
defined by a 1-metre ice thickness threshold.
""")


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    out_file = 'processed/alpero.{}.{}.{}.agg.nc'.format(
        res, rec[:4], 'pp' if 'pp' in other else 'cp')

    # load output data (in the future combine='by_coords' will be the default)
    print("postprocessing " + out_file + "...")
    boot = hyoga.open.dataset(
        '~/pism/input/boot/'+'alps.srtm.hus12.gou11simi.{}.nc'.format(res))
    print("* reading multi-file extra dataset...")
    ex = hyoga.open.mfdataset(run_path+'/ex.???????.nc', parallel=True)

    # init postprocessed dataset with global attributes
    pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))
    pp.attrs.update(
        subtitle='{} {} simulation {} precipitation reductions'.format(
            res, rec.upper(), 'with' if 'pp' in other else 'without'),
        **GLOB_ATTRS)
    pp.attrs.update(history=pp.command+pp.history)

    # register intermediate variables (I assumed the K_g numbers given in
    # supplement of Koppes et al., 2015 are for erosion rates in mm/a. An
    # alternative formula with two outliers removed gives 5.3e−12*v_b*2.62
    # (m/a). Now for some reason, these erosion laws seem to not exactly
    # correspond to the blue and pink lines on the summary figure by Cook et
    # al., 2020, which appear to be a factor two or three lower.)
    ex['icy'] = (ex.thk >= 1.0)
    ex['bedlift'] = ex.topg - boot.topg.where(boot.topg > 0, 0)
    ex['sliding'] = ex.velbase_mag.where(ex.icy)
    ex['warmbed'] = ex.icy*(ex.temppabase >= -1e-3)
    ex['coo2020'] = (1.665e-4*ex.sliding**0.6459).assign_attrs(
        ref='Cook et al. (2020)', units='m a-1')
    ex['her2015'] = (2.7e-7*ex.sliding**2.02).assign_attrs(
        ref='Herman et al. (2015)', units='m a-1')
    ex['hum1994'] = (1e-4*ex.sliding).assign_attrs(
        ref='Humphrey and Raymond (1994)', units='m a-1')
    ex['kop2015'] = (5.2e-11*ex.sliding**2.34).assign_attrs(
        ref='Koppes et al. (2015)', units='m a-1')

    # compute grid size
    dt = ex.age[0] - ex.age[1]
    dt = dt*1e3  # convert ka to a
    dx = ex.x[1] - ex.x[0]
    dy = ex.y[1] - ex.y[0]

    # compute glacial cycle integrated variables
    pp['cumu_sliding'] = (dt*ex.sliding.sum(axis=0, min_count=1)).assign_attrs(
        long_name='cumulative basal motion', units='m')
    pp['glacier_time'] = (dt*ex.icy.sum(axis=0)).assign_attrs(
        long_name='total ice cover duration', units='years')
    pp['warmbed_time'] = (dt*ex.warmbed.sum(axis=0)).assign_attrs(
        long_name='temperate-based ice cover duration', units='years')

    # trigger computation to avoid memory errors (18m, 70%, 8GiB)
    # NOTE: time and total mem for single-thread scheduler on altair, with
    # nothing else running. Trigger compute() more often to further reduce mem
    # consumption (maybe at the cost of repeating some operations).
    print("* computing time-integrated variables...")
    with dask.diagnostics.ProgressBar():
        pp = pp.compute()

    # compute timeseries
    pp['glacier_area'] = (dx*dy*ex.icy.sum(axis=(1, 2))).assign_attrs(
        long_name='glacierized area', units='m2')
    pp['volumic_lift'] = (dx*dy*ex.bedlift.sum(axis=(1, 2))).assign_attrs(
        long_name='volumic bedrock uplift', units='m3')
    pp['warmbed_area'] = (dx*dy*ex.warmbed.sum(axis=(1, 2))).assign_attrs(
        long_name='temperate-based ice cover area', units='m2')

    # trigger computation to avoid memory errors (24m, 35%, 4GiB)
    print("* computing space-integrated variables...")
    with dask.diagnostics.ProgressBar():
        pp = pp.compute()

    # compute erosion time-aggregated variables
    for law in ['coo2020', 'her2015', 'hum1994', 'kop2015']:
        pp[law+'_cumu'] = (dt*ex[law].sum(axis=0, min_count=1)).assign_attrs(
            long_name=ex[law].ref+' cumulative glacial erosion potential',
            units='m')

    # trigger computation to avoid memory errors (12m, 35%, 4GiB)
    print("* computing cumulative erosion potential...")
    with dask.diagnostics.ProgressBar():
        pp = pp.compute()

    # compute erosion space-aggregated variables
    # there's still a divide warning here, maybe check what that is
    # NOTE: for the 1-km-run hypsogram on 10-m bands, dask-2021.3.0 splits the
    # chunks even when asked not to. The progress bar only appears after two
    # hours (I nearly gave up), but the actual computations takes only 15 min!
    # In total the script took 194 min on altair.
    x, y = cpf.read_shp_coords(
        '../data/native/profile_rhine.shp', interval=1000)
    for law in ['coo2020', 'her2015', 'hum1994', 'kop2015']:
        pp[law+'_rate'] = (dx*dy*ex[law].sum(axis=(1, 2))).assign_attrs(
            long_name=ex[law].ref+' domain total volumic erosion rate',
            units='m3 year-1')
        pp[law+'_hyps'] = np.exp(np.log(ex[law]).groupby_bins(
            boot.topg, bins=range(0, 4501, 100)).mean(
                dim='stacked_y_x')).assign_attrs(
            long_name=ex[law].ref+' erosion rate geometric mean in band',
            units='m year-1')
        pp[law+'_rhin'] = ex[law].where(ex.icy).interp(
                x=x, y=y, method='linear').assign_attrs(
            long_name=ex[law].ref+' rhine transect erosion rate',
            units='m year-1')

    # trigger computation to avoid memory errors (12m, 40%, 5GiB)
    print("* computing erosion rate variables...")
    with dask.diagnostics.ProgressBar():
        pp = pp.compute()

    # compute glacier cover hypsogram
    pp['glacier_hyps'] = (
        dx*dy*ex.icy.groupby_bins(boot.topg, bins=range(0, 4501, 100)).sum(
            dim='stacked_y_x')).assign_attrs(
        long_name='glacierized area within elevation band', units='m2')

    # trigger computation to avoid memory errors (6m, 40%, 5GiB)
    print("* computing glacier cover hypsogram...")
    with dask.diagnostics.ProgressBar():
        pp = pp.compute()

    # replace intervals (xarray issue #2847)
    pp['topg_bins'] = [b.mid for b in pp.topg_bins.values]
    pp = pp.rename({'topg_bins': 'z'})
    pp['z'] = pp.z.assign_attrs(
        long_name='elevation band midpoints', units='m')
    pp['d'] = pp.d.assign_attrs(
        long_name='distance along transect', units='m')

    # copy grid mapping and pism config
    pp['mapping'] = ex.mapping
    pp['pism_config'] = ex.pism_config

    # export to netcdf
    print("* writing postprocessed file...")
    delayed = pp.to_netcdf(
        out_file, mode='w', compute=False, encoding={var: dict(
            zlib=True, shuffle=True, complevel=1) for var in pp.variables})
    with dask.diagnostics.ProgressBar():
        delayed.compute()

    # close datasets
    boot.close()
    ex.close()
    pp.close()


def main():
    """Main program called during execution."""

    # create directory if missing
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # to use the dask distributed client
    # client = dask.distributed.Client()
    # print(client.dashboard_link)

    # ask dask to not split large chunks (but it still does)
    dask.config.set(**{'array.slicing.split_large_chunks': False})

    # postprocess selected runs
    for run in PROC_RUNS:
        postprocess_extra(os.environ['HOME'] + '/pism/output/e9d2d1f/' + run)


if __name__ == '__main__':
    main()
