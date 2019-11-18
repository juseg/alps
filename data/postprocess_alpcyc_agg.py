#!/usr/bin/env python
# Copyright (c) 2018-2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPCYC aggregated variables."""

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
    title='Alpine ice sheet glacial cycle simulations aggregated variables',
    author='Julien Seguinot',
    institution='ETH Zürich, Switzerland and Hokkaido University, Japan',
    command='{user}@{host} {time}: {cmdl}\n'.format(
        user=os.environ['USER'], host=os.uname()[1], cmdl=' '.join(sys.argv),
        time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')),
    comment="""Aggregated dataset contents:
* Maximum extent (maxext*) variables correspond to a snapshot of model output
  at the age of maximum glacierized area, indicated by their age attributes.
* Maximum thickness (maxthk*) variables are time-transgressive and correspond
  to the age of maximum ice thickness in each grid cell, given by the maximum
  thickness age (maxthkage) variable.
* Other variables are numerically integrated over the last glacial cycle.
""")


def get_maxext_time(run_path):
    """Get accurate max extent time from ts files."""
    with xr.open_mfdataset(run_path+'/ts.???????.nc', decode_times=False,
                           chunks=dict(time=50), combine='by_coords') as ts:
        return ts.time[ts.area_glacierized.argmax(axis=0).data]


def postprocess_extra(run_path):
    """Postprocess extra dataset for one run."""

    # output file and subtitle
    _, res, rec, *other = os.path.basename(run_path).split('.')
    boot_file = (os.environ['HOME'] + '/pism/input/boot/' +
                 'alps.srtm.hus12.gou11simi.{}.nc'.format(res))
    out_file = 'processed/alpcyc.{}.{}.{}.agg.nc'.format(
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

    # init postprocessed dataset with global attributes
    pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))
    pp.attrs.update(subtitle=subtitle, **GLOB_ATTRS)
    pp.attrs.update(history=pp.command+pp.history)

    # register intermediate variables
    ex['age'] = (ex.time/(-365.0*24*60*60)).assign_attrs(units='years')
    ex['icy'] = (ex.thk >= 1.0)

    # compute grid size
    dt = ex.age[0] - ex.age[1]

    # compute glacial cycle integrated variables
    pp['covertime'] = (dt*ex.icy.sum(axis=0)).assign_attrs(
        long_name='ice cover duration', units='years')
    idx = ex.icy[::-1].argmax(axis=0).compute()
    pp['deglacage'] = (ex.age[-idx].where(idx > 0)).assign_attrs(
        long_name='deglaciation age', units='years')
    pp['footprint'] = (pp.covertime > 0.0).assign_attrs(
        long_name='glaciated area', units='')

    # compute max extent snapshot variables
    idx = abs(ex.time-get_maxext_time(run_path)).argmin()
    ice = ex.icy[idx]
    attrs = dict(age=ex.age[idx].data, age_units=ex.age.units,
                 time=ex.time[idx].data, time_units=ex.time.units)
    pp['maxextthk'] = (ex.thk[idx].where(ice)).assign_attrs(
        long_name='maximum extent ice thickness', **attrs)
    pp['maxextbtp'] = (ex.temppabase[idx].where(ice)).assign_attrs(
        long_name='maximum extent pressure-adjusted basal temperature', **attrs)
    pp['maxextbtt'] = (ex.tempicethk_basal[idx].where(ice)).assign_attrs(
        long_name='maximum extent basal temperate ice layer thickness', **attrs)
    pp['maxextbvx'] = (ex.uvelbase[idx].where(ice)).assign_attrs(
        long_name='maximum extent basal velocity x-component', **attrs)
    pp['maxextbvy'] = (ex.vvelbase[idx].where(ice)).assign_attrs(
        long_name='maximum extent basal velocity y-component', **attrs)
    pp['maxextsrf'] = (ex.usurf[idx].where(ice)).assign_attrs(
        long_name='maximum extent ice surface elevation', **attrs)
    pp['maxextsvx'] = (ex.uvelsurf[idx].where(ice)).assign_attrs(
        long_name='maximum extent surface velocity x-component', **attrs)
    pp['maxextsvy'] = (ex.vvelsurf[idx].where(ice)).assign_attrs(
        long_name='maximum extent surface velocity y-component', **attrs)
    pp['maxexttpg'] = (ex.topg[idx]).assign_attrs(
        long_name='maximum extent bedrock topography', **attrs)

    # compute max thickness transgressive variables
    # (note: first version ice mask was wrongly set to max extent mask)
    ice = pp.footprint
    idx = ex.thk.argmax(dim='time').compute()  # xarray issue #2511
    pp['maxthkage'] = (ex.age[idx].where(ice)).assign_attrs(
        long_name='maximum thickness age')
    pp['maxthkbtp'] = (ex.temppabase[idx].where(ice)).assign_attrs(
        long_name='maximum thickness pressure-adjusted basal temperature')
    pp['maxthkbtt'] = (ex.tempicethk_basal[idx].where(ice)).assign_attrs(
        long_name='maximum thickness basal temperate ice layer thickness')
    pp['maxthkbvn'] = (ex.velbase_mag[idx].where(ice)).assign_attrs(
        long_name='maximum thickness basal velocity norm')
    pp['maxthksrf'] = (ex.usurf[idx].where(ice)).assign_attrs(
        long_name='maximum thickness ice surface elevation')
    pp['maxthkthk'] = (ex.thk[idx].where(ice)).assign_attrs(
        long_name='maximum ice thickness')

    # compute mis 2 and 4 footprints
    covertime = ex.icy[(14e3 < ex.age) & (ex.age < 29e3)].sum(axis=0)
    pp['mis2print'] = (covertime > 0).assign_attrs(
        long_name='glaciated area between 29 and 14 ka', units='')
    covertime = ex.icy[(57e3 < ex.age) & (ex.age < 71e3)].sum(axis=0)
    pp['mis4print'] = (covertime > 0).assign_attrs(
        long_name='glaciated area between 71 and 57 ka', units='')

    # copy boot variables
    with xr.open_dataset(boot_file, decode_cf=False, decode_times=False,
                         ) as boot:
        pp['inicdtthk'] = boot.thk.T.assign_attrs(
            long_name='initial condiction ice thickness')
        pp['inicdttpg'] = boot.topg.T.assign_attrs(
            long_name='initial condiction bedrock surface elevation')

    # copy grid mapping and pism config
    pp['mapping'] = ex.mapping
    pp['pism_config'] = ex.pism_config

    # export to netcdf
    pp.to_netcdf(out_file, mode='w', encoding={var: dict(
        zlib=True, shuffle=True, complevel=1) for var in pp.variables})

    # close datasets
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
