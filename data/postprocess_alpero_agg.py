#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Prepare ALPERO aggregated variables."""

import os
import sys
import datetime
import xarray as xr

# Global parameters
# -----------------

# add global attributes
globs = dict(
    title='Alpine ice sheet glacial cycle erosion aggregated variables',
    author='Julien Seguinot',
    institution='ETH Zürich, Switzerland and Hokkaido University, Japan',
    command='{user}@{host} {time}: {cmdl}\n'.format(
        user=os.environ['USER'], host=os.uname()[1], cmdl=' '.join(sys.argv),
        time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')))


# Loop on selected run
# --------------------


def postprocess(ipath, ofile, subtitle):

    # Load model output
    # -----------------

    # load output data (in the future combine='by_coords' will be the default)
    print("loading " + ipath + "...")
    ts = xr.open_mfdataset(
        ipath+'/ts.???????.nc', combine='by_coords', decode_times=False)
    ex = xr.open_mfdataset(
        ipath+'/ex.???????.nc', combine='by_coords', decode_times=False,
        chunks={'time': 50}, data_vars='minimal')

    # get global attributes from last file (netcdf4 issue #835)
    last = xr.open_dataset(ipath+'/ex.0120000.nc', decode_times=False)
    ex.attrs = last.attrs
    last.close()

    # create age coordinate and extract time step
    ex['age'] = -ex['time']/(365.0*24*60*60)
    ex['age'].attrs['units'] = 'years'
    dt = ex['age'][0] - ex['age'][1]

    # init postprocessed dataset with global attributes
    pp = xr.Dataset(attrs=ex.attrs, coords=dict(lon=ex.lon, lat=ex.lat))

    # Compute aggregated variables
    # ----------------------------

    # registering proxy variables
    ex['icy'] = (ex.thk >= 1.0)
    ex['ero'] = 2.7e-7*(ex.icy*ex.velbase_mag)**2.02  # m/a (Herman etal, 2015)
    ex['warm'] = ex.icy*(ex.temppabase >= -1e-3)

    # compute index of last basal velocity
    print("* computing index of last basal velocity...")
    i = (ex.icy*(ex.velbase_mag >= 1.0))[::-1].argmax(axis=0).compute()

    # compute last basal velocity transgressive variables
    ln = 'last basal velocity age'
    print("* computing " + ln + "...")
    pp['lastbvage'] = ex.age[-i].where(i > 0).compute()
    pp['lastbvage'].attrs = dict(long_name=ln, grid_mapping='mapping',
                                 units=ex.age.units)
    ln = 'last basal velocity x-component'
    print("* computing " + ln + "...")
    pp['lastbvbvx'] = ex.uvelbase[-i].where(i > 0).compute()
    pp['lastbvbvx'].attrs = dict(long_name=ln, grid_mapping='mapping',
                                 units=ex.uvelbase.units)
    ln = 'last basal velocity y-component'
    print("* computing " + ln + "...")
    pp['lastbvbvy'] = ex.vvelbase[-i].where(i > 0).compute()
    pp['lastbvbvy'].attrs = dict(long_name=ln, grid_mapping='mapping',
                                 units=ex.vvelbase.units)

    # compute glacial cycle integrated variables
    ln = 'cumulative basal motion'
    print("* computing " + ln + "...")
    pp['totalslip'] = (ex.icy*ex.velbase_mag).sum(axis=0).compute()*dt
    pp['totalslip'].attrs = dict(long_name=ln, grid_mapping='mapping',
                                 units='m')
    ln = 'cumulative glacial erosion'
    print("* computing " + ln + "...")
    pp['glerosion'] = ex.ero.sum(axis=0).compute()*dt
    pp['glerosion'].attrs = dict(long_name=ln, grid_mapping='mapping',
                                 units='m year-1')
    ln = 'temperate-based ice cover duration'
    print("* computing " + ln + "...")
    pp['warmcover'] = ex.warm.sum(axis=0).compute()*dt
    pp['warmcover'].attrs = dict(long_name=ln, grid_mapping='mapping',
                                 units='years')

    # add global attributes
    pp.attrs.update(globs)
    pp.attrs['subtitle'] = subtitle
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
    print("* exporting aggregated data...")
    pp.drop('time')
    pp.to_netcdf(ofile, mode='w',
                 encoding={var: {'zlib': True, 'shuffle': True, 'complevel': 5}
                           for var in pp.variables})

    # close datasets
    ex.close()
    pp.close()
    ts.close()


def main():
    """Main program called during execution."""

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
        conf = ('.pp' if dp == 'pp' else '')

        # input and output file paths
        rname = 'alpcyc4.{}.{}.{:04.0f}{}'.format(res, rec, 100*dt, conf)
        ipath = os.environ['HOME'] + '/pism/output/e9d2d1f/' + rname
        ofile = 'processed/alpero.{}.{}.{}.agg.nc'.format(res, rec[:4], dp)
        subtitle = ('{} {} simulation '.format(res, rec.upper()) +
                    ('with ' if dp == 'pp' else 'without ') +
                    'precipitation reductions')
        subtitle = '{} {} simulation {} precipitation reductions'.format(
            res, rec.upper(), 'with' if dp == 'pp' else 'without')
        postprocess(ipath, ofile, subtitle)


if __name__ == '__main__':
    main()
