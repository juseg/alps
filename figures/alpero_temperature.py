#!/usr/bin/env python
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion ice temperature profiles."""

import matplotlib.pyplot as plt
import cartowik.profiletools as cpf
import absplots as apl
import pismx.open


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(177, 80), nrows=3, sharex=True, sharey=True, gridspec_kw=dict(
            left=12, right=18, bottom=9, top=1.5, hspace=1.5))
    cax = fig.add_axes_mm([177-18+1.5, 9, 3, 80-10.5])

    # run and time for plot
    run = '~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp'
    ages = [24, 20, 16]

    # read profile coordinates
    x, y = cpf.read_shp_coords(
        '../data/native/profile_rhine.shp', interval=1e3)

    # loop on ages
    for ax, age in zip(axes, ages):
        ax.set_rasterization_zorder(2.5)

        # open 3d output data
        with pismx.open.dataset(
                '{}/out.{:07.0f}.nc'.format(run, (120-age)*1e3)) as ds:

            # interpolate along profile, use km, remove age
            ds = ds[['topg', 'usurf', 'temp_pa']]
            ds = ds.interp(x=x, y=y, method='linear')
            ds = ds.assign_coords(d=ds.d/1e3).squeeze()

            # plot topographic profiles
            ds.topg.plot(ax=ax, x='d', color='k', lw=0.5)
            ds.usurf.plot(ax=ax, x='d', color='k', lw=0.5)
            #    ax.plot(dp, (bp+wp).T, 'k-', lw=0.5)

            # mask temps above ice surface
            ds['temp_pa'] = ds.temp_pa.where(ds.topg+ds.z < ds.usurf)

            # plot temperature profile
            cset = ax.contourf(
                ds.d.expand_dims(z=ds.z), ds.z+ds.topg, ds.temp_pa, alpha=0.75,
                levels=range(-24, 1, 3), cmap='RdBu_r', extend='both')

        # open 2d extra data
        with pismx.open.dataset(
                '{}/ex.{:07.0f}.nc'.format(run, (120-age)*1e3)) as ds:

            # interpolate along profile, use km, remove age, get cold base
            ds = ds[['thk', 'topg', 'tempicethk_basal', 'temppabase']]
            ds = ds.tail(age=1).interp(x=x, y=y, method='linear')
            ds = ds.assign_coords(d=ds.d/1e3).squeeze()

            # intermediate variables
            ds['coldbase'] = (ds.temppabase < -1e-6) * (ds.thk > 1)
            ds['meltline'] = ds.topg + ds.tempicethk_basal

            # plot temperate layer and cold base
            ds.meltline.plot(ax=ax, x='d', color='k', lw=0.5)
            ax.fill_between(
                ds.d, ds.topg, ds.meltline, color=plt.get_cmap('RdBu')(0),
                alpha=0.75, label='temperate ice layer')
            ax.fill_between(
                ds.d, ds.topg.where(ds.coldbase)-250,
                ds.topg.where(ds.coldbase), edgecolor='k', facecolor='none',
                hatch='//////', label='cold-based areas')

            # IDEA: plot melt rates e.g.
            # ax.plot(
            #    ds.d, ds.topg+ds.melt.where(ds.melt > 0)*10,
            #    color='k', dashes=(2, 1), label='annual melt x10')

        # add age tag
        ax.set_title('')
        ax.set_ylabel('elevation (m)')
        ax.text(0.02, 0.1, '{:.0f} ka'.format(age), fontweight='bold',
                ha='left', va='bottom', transform=ax.transAxes)

    # set axes properties
    ax = axes[-1]
    ax.set_ylim(-250, 3250)
    ax.set_xlabel('distance along flow (km)')
    ax.set_ylabel('elevation (m)')
    ax.legend()

    # add colorbar
    cbar = fig.colorbar(cset, cax)
    cbar.set_label(u'temperature below melting point (°C)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
