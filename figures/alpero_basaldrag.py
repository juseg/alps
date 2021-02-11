#!/usr/bin/env python
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion change in glacier slope."""

import cartowik.profiletools as cpf
import cartowik.decorations as cde
import absplots as apl
import pismx.open


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(85, 80), nrows=2, sharex=True, gridspec_kw=dict(
            left=12, right=1.5, bottom=9, top=1.5, hspace=1.5))
    for ax, label in zip(axes, 'ab'):
        cde.add_subfig_label('(%s)' % label, ax=ax, loc='sw')

    # read profile coordinates
    x, y = cpf.read_shp_coords(
        '../data/native/profile_rhine.shp', interval=1e3)

    # each requested age
    for age in [24, 20, 16]:
        with pismx.open.subdataset(
                ('~/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp'
                 '/ex.{:07.0f}.nc'), time=-age*1e3, shift=120000) as ds:

            # interpolate along profile, use km
            ds = ds.interp(x=x, y=y, method='linear')
            ds = ds.assign_coords(d=ds.d/1e3)

            # plot topographic profiles
            ds['usurf'] = ds.topg + ds.thk.fillna(0)
            ds.usurf.plot.line(ax=axes[0], x='d', label='{} ka'.format(age))
            ds.topg.plot.line(ax=axes[0], x='d', color='0.25')

            # plot normalized stresses
            overburden = 910 * 9.81 * ds.thk.where(ds.thk > 1)
            (ds.tauc/overburden*100).plot.line(
                ax=axes[1], x='d', c='0.25', ls=':',
                label='yield stress / overburden' if age == 24 else None)
            ((ds.taub_x**2+ds.taub_y**2)**0.5/overburden*100).plot.line(
                ax=axes[1], x='d',
                label='basal drag / overburden' if age == 24 else None)

            # to plot driving stress
            # taud = ((ds.taud_x**2+ds.taud_y**2)**0.5/overburden*100)
            # taud.load().rolling(d=50, center=True).mean().plot.line(
            #     ax=axes[1], x='d', ls='-', add_legend=False)

    # set axes properties
    axes[0].set_ylabel('elevation (m)')
    axes[0].set_title('')
    axes[0].legend()

    # set axes properties
    axes[1].set_xlabel('distance along flow (km)')
    axes[1].set_ylabel('normalized stress (%)')
    axes[1].set_ylim(0, 3)
    axes[1].set_title('')
    axes[1].legend()

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
