#!/usr/bin/env python2
# coding: utf-8

"""Prepare ALPCYC aggregated variables."""

import os
import sys
import datetime
import xarray as xr

# Global parameters
# -----------------

# add global attributes
globs = dict(
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

# mapping between 3-char variable names and pism variable names
pism_names = dict(age='age', btp='temppabase', btt='tempicethk_basal',
                  bvn='velbase_mag', bvx='uvelbase', bvy='vvelbase',
                  svn='velsurf_mag', svx='uvelsurf', svy='vvelsurf',
                  thk='thk', tpg='topg', srf='usurf')

# mapping between 3-char variable names and long names in output file
long_names = dict(age='age',
                  btp='pressure-adjuste basal temperature',
                  btt='basal temperate ice layer thickness',
                  bvn='basal velocity norm',
                  bvx='basal velocity x-component',
                  bvy='basal velocity y-component',
                  svn='surface velocity norm',
                  svx='surface velocity x-component',
                  svy='surface velocity y-component',
                  srf='ice surface elevation',
                  thk='ice thickness',
                  tpg='basal topography')


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
    rname = 'alps-wcnn-{}/{}3222cool{:04.0f}+{}'.format(res, rec, 100*dt, conf)
    ipath = os.environ['HOME'] + '/pism/output/e9d2d1f/' + rname
    ofile = 'processed/alpcyc.{}.{}.{}.agg.nc'.format(res, rec[:4], dp)


    # Load model output
    # -----------------

    # load output data
    print "loading " + rname + "..."
    ts = xr.open_mfdataset(ipath+'/y???????-ts.nc', decode_times=False)
    ex = xr.open_mfdataset(ipath+'/y???????-extra.nc', decode_times=False,
                           chunks={'time': 50}, data_vars='minimal')

    # get global attributes from last file (xarray issue #2382)
    last = xr.open_dataset(ipath+'/y0120000-extra.nc', decode_times=False)
    ex.attrs = last.attrs
    last.close()

    # register proxy variables and extract time step
    ex['icy'] = (ex.thk >= 1.0).assign_attrs(units='')
    ex['age'] = (-ex['time']/365/24/60/60).assign_attrs(units='years')
    dt = ex['age'][0] - ex['age'][1]

    # init postprocessed dataset with global attributes
    pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))


    # Compute aggregated variables
    # ----------------------------

    # compute index of max ice extent
    a = 24556.0  # max of slvol and volume_glacierized (1km)
    a = 24568.0  # max of area_glacierized (1km)
    t = ts.time[ts.area_glacierized.argmax(dim='time').compute()]
    i = abs(ex.time-t).argmin()  # could also use ex.sel()
    age_attrs = dict(age=ex.age[i].data, age_units=ex.age.units,
                     time=ex.time[i].data, time_units=ex.time.units)

    # compute max extent snapshot variables
    for var in ['thk', 'btp', 'btt', 'bvx', 'bvy', 'srf', 'svx', 'svy', 'tpg']:
        attrs = dict(long_name='maximum extent ' + long_names[var], **age_attrs)
        print "* computing {long_name} ...".format(**attrs)
        pp['maxext'+var] = ex[pism_names[var]][i].compute().assign_attrs(attrs)
        if var != 'tpg':
            pp['maxext'+var] = pp['maxext'+var].where(pp.maxextthk >= 1.0)

    # compute index of max ice thickness
    print "* computing index of maximum ice thickness..."
    i = ex['thk'].argmax(dim='time').compute()

    # compute max thickness transgressive variables
    for var in ['thk', 'age', 'btp', 'btt', 'bvn', 'srf']:
        attrs = dict(long_name='maximum thickness ' + long_names[var])
        print "* computing {long_name} ...".format(**attrs)
        pp['maxthk'+var] = ex[pism_names[var]][i].compute().assign_attrs(attrs)
        pp['maxthk'+var] = pp['maxthk'+var].where(pp.maxthkthk >= 1.0)

    # compute glacial cycle integrated variables
    attrs = dict(long_name='ice cover duration', units='years')
    print "* computing {long_name} ...".format(**attrs)
    pp['covertime'] = ex.icy.sum(axis=0).compute().assign_attrs(attrs)*dt
    attrs = dict(long_name='deglaciation age', units='years')
    print "* computing {long_name} ...".format(**attrs)
    i = ex.icy[::-1].argmax(axis=0).compute()
    pp['deglacage'] = ex.age[-i].where(i > 0)
    attrs = dict(long_name='ice cover footprint', units='')
    print "* computing {long_name} ...".format(**attrs)
    pp['footprint'] = (pp.covertime > 0.0).compute().assign_attrs(attrs)

    # add global attributes
    pp.attrs.update(globs)
    pp.attrs['subtitle'] = ('{} {} simulation '.format(res, rec.upper()) +
                            ('with ' if dp == 'pp' else 'without ') +
                            'precipitation reductions')
    pp.attrs['history'] = pp.attrs['command'] + pp.attrs['history']

    # copy grid mapping and pism config
    pp['mapping'] = ex.mapping
    pp['pism_config'] = ex.pism_config


    # Export aggregated data
    # ----------------------

    # create directory if missing
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # export to netcdf
    print "* exporting aggregated data..."
    pp.drop('time')
    pp.to_netcdf(ofile, mode='w',
                 encoding={var: {'zlib': True, 'shuffle': True, 'complevel': 5}
                           for var in pp.variables})

    # close datasets
    ex.close()
    pp.close()
    ts.close()
