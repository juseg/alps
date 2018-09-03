#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated variables."""

import os
import sys
import datetime
from dask.diagnostics import ProgressBar
import xarray as xr


def message(**attrs):
    """Print a message and pass variables attributes."""
    print "* preparing {long_name} ...".format(**attrs)
    return attrs


# Loop on selected run
# --------------------

# loop on selected runs
gridres = ['2km']*6 + ['1km']
records = ['grip']*2 + ['epica']*2 + ['md012444']*2 + ['epica']
pparams = ['cp', 'pp']*3 + ['pp']
offsets = [8.2, 10.4, 9.7, 12.2, 8.0, 10.6, 12.2]
for i in range(7):
    res = gridres[i]
    rec = records[i]
    dp = pparams[i]
    dt = offsets[i]
    conf = 'alpcyc4' + ('+pp' if dp == 'pp' else '')

    # input and output file paths
    pism_dir = os.path.join(os.environ['HOME'], 'pism')
    boot_file = pism_dir + '/input/boot/alps-srtm+thk+gou11simi-' + res + '.nc'
    dt_file = '{}3222cool{:04.0f}'.format(rec, 100*dt)
    run_dir = '{}/output/e9d2d1f/alps-wcnn-{}/{}+alpcyc4{}'.format(
        pism_dir, res, dt_file, '+pp' if dp == 'pp' else '')
    ex_file = run_dir + '/y???????-extra.nc'
    ts_file = run_dir + '/y???????-ts.nc'
    pp_file = 'processed/alpcyc.{}.{}.{}.agg.nc'.format(res, rec[:4], dp)

    # Load model output
    # -----------------

    # open output data
    print "loading " + run_dir + "..."
    with xr.open_mfdataset(ex_file, concat_dim='time',
                           chunks=dict(time=10), decode_cf=False,
                           decode_times=False, data_vars='minimal') as ex:

        # get global attributes from last file (xarray issue #2382)
        with xr.open_dataset(ex_file.replace('???????', '0120000'),
                             decode_times=False) as ds:
            ex.attrs = ds.attrs
            ds.close()

        # register proxy variables and extract time step
        ex['icy'] = (ex.thk >= 1.0).assign_attrs(units='')
        ex['age'] = (-ex['time']/365/24/60/60).assign_attrs(units='years')
        dt = ex['age'][0] - ex['age'][1]

        # init postprocessed dataset with global attributes
        pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))

        # Compute aggregated variables
        # ----------------------------

        # compute glacial cycle integrated variables
        attrs = message(long_name='ice cover duration', units='years')
        pp['covertime'] = ex.icy.sum(axis=0).assign_attrs(attrs)*dt
        attrs = message(long_name='deglaciation age', units='years')
        i = ex.icy[::-1].argmax(axis=0).compute()
        pp['deglacage'] = ex.age[-i].where(i > 0).assign_attrs(attrs)
        attrs = message(long_name='ice cover footprint', units='')
        pp['footprint'] = (pp.covertime > 0.0).assign_attrs(attrs)

        # compute index of max ice extent
        with xr.open_mfdataset(ts_file, decode_times=False) as ds:
            time = ds.time[ds.area_glacierized.argmax(axis=0).data]
        i = abs(ex.time-time).argmin()  # could also use ex.sel()

        # compute max extent snapshot variables
        prefix = 'maximum extent '
        ice = ex.icy[i]
        attrs = message(long_name=prefix+'ice thickness')
        pp['maxextthk'] = ex.thk[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'pressure-adjusted basal temperature')
        pp['maxextbtp'] = ex.temppabase[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'basal temperate ice layer thickness')
        pp['maxextbtt'] = ex.tempicethk_basal[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'basal velocity x-component')
        pp['maxextbvx'] = ex.uvelbase[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'basal velocity y-component')
        pp['maxextbvy'] = ex.vvelbase[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'ice surface elevation')
        pp['maxextsrf'] = ex.usurf[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'surface velocity x-component')
        pp['maxextsvx'] = ex.uvelsurf[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'surface velocity y-component')
        pp['maxextsvy'] = ex.vvelsurf[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'bedrock topography')
        pp['maxexttpg'] = ex.topg[i].assign_attrs(attrs)

        # add age attributes
        age_attrs = dict(age=ex.age[i].data, age_units=ex.age.units,
                         time=ex.time[i].data, time_units=ex.time.units)
        for name, variable in pp.variables.iteritems():
            if name.startswith('maxext'):
                variable.attrs.update(age_attrs)

        # compute max thickness transgressive variables
        prefix = 'maximum thickness '
        icy = pp.footprint
        attrs = message(long_name=prefix+'age')
        i = ex.thk.argmax(dim='time').compute()
        pp['maxthkage'] = ex.age[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'pressure-adjusted basal temperature')
        pp['maxthkbtp'] = ex.temppabase[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'basal temperate ice layer thickness')
        pp['maxthkbtt'] = ex.tempicethk_basal[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'basal velocity norm')
        pp['maxthkbvn'] = ex.velbase_mag[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name=prefix+'ice surface elevation')
        pp['maxthksrf'] = ex.usurf[i].where(ice).assign_attrs(attrs)
        attrs = message(long_name='maximum ice thickness')
        pp['maxthkthk'] = ex.thk[i].where(ice).assign_attrs(attrs)

        # copy grid mapping and pism config
        pp['mapping'] = ex.mapping
        pp['pism_config'] = ex.pism_config

    # Copy boot variables
    # -------------------

    # open boot file
    with xr.open_dataset(boot_file, decode_cf=False, decode_times=False) as ds:

        # copy variables
        prefix = 'initial condition '
        attrs = message(long_name=prefix+'ice thickness')
        pp['inicdtthk'] = ds.thk.T.assign_attrs(attrs)
        attrs = message(long_name=prefix+'bedrock surface elevation')
        pp['inicdttpg'] = ds.topg.T.assign_attrs(attrs)

    # Add attributes
    # --------------

    # remove outdated variable attributes
    for name, variable in pp.variables.iteritems():
        variable.attrs.pop('coordinates', None)
        variable.attrs.pop('pism_intent', None)

    # add global attributes
    pp.attrs.update(
        author='Julien Seguinot',
        institution='ETH Zürich, Switzerland and Hokkaido University, Japan',
        title=('Alpine ice sheet glacial cycle simulations '
               'aggregated variables'),
        subtitle='{res} {rec} simulation {w} precipitation reductions'.format(
            res=res, rec=rec.upper(), w='with' if dp == 'pp' else 'without'),
        command='{user}@{host} {time}: {cmdl}\n'.format(
            user=os.environ['USER'],
            host=os.uname()[1],
            cmdl=' '.join(sys.argv),
            time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')),
        comment="""Aggregated dataset contents:
* Maximum extent (maxext*) variables correspond to a snapshot of model output
  at the age of maximum glacierized area, indicated by their age attributes.
* Maximum thickness (maxthk*) variables are time-transgressive and correspond
  to the age of maximum ice thickness in each grid cell, given by the maximum
  thickness age (maxthkage) variable.
* Other variables are numerically integrated over the last glacial cycle.
""")

    # append history
    pp.attrs['history'] = pp.attrs['command'] + pp.attrs['history']

    # Export aggregated data
    # ----------------------

    # create directory if missing
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # export to netcdf
    print "* exporting aggregated data..."
    pp = pp.drop('time')
    encoding = dict(zlib=True, shuffle=True, complevel=5)
    encoding = {var: encoding for var in pp.variables}
    with ProgressBar():
        pp.to_netcdf(pp_file, mode='w', encoding=encoding)
