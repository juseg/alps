#!/usr/bin/env python
# coding: utf-8

import os
import util
import matplotlib.pyplot as plt
import cartowik.profiletools as cpf

# parameters
regions = ['rhine', 'rhone', 'ivrea', 'isere', 'inn', 'taglia']
labels = ['Rhine', 'Rhone', 'Dora Baltea', u'Isère', 'Inn', 'Tagliamento']

# initialize figure
fig, grid, tsgrid = util.fig.subplots_profiles(regions, labels)

# load extra data in memory (interp on dask array takes 12min per profile)
# FIXME postprocess profile data?
filename = os.environ['HOME'] + '/pism/' + util.alpcyc_bestrun + 'ex.???????.nc'
with util.io.open_mfdataset(filename) as ds:
    thk = ds.thk[9::10].compute()

# loop on regions
for i, reg in enumerate(regions):
    c = plt.get_cmap('Paired').colors[2*i+1]  # 'C11' is not a valid name
    ax = grid[i]
    tsax = tsgrid[i]
    label = labels[i]

    # Map axes
    # --------

    # load aggregated data
    with util.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
        srf = ds.maxthksrf
        ext = ds.maxthksrf.notnull()

        # plot surface contours and footprint
        ext.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors='w',
                          extend='neither', levels=[0.5, 1.5])
        ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.25)

    # remove title from xarray
    ax.set_title('')

    # add map elements
    util.pl.draw_boot_topo(ax)
    util.geo.draw_natural_earth(ax)
    util.geo.draw_lgm_outline(ax)

    # add profile line from shapefile
    xp, yp = cpf.read_shp_coords('../data/native/profile_'+reg+'.shp')
    ax.plot(xp, yp, c=c, dashes=(2, 1))
    ax.plot(xp[0], yp[0], c=c, marker='o')


    # Time series
    # -----------

    # interpolate thickness and plot envelope
    hp = thk.interp(x=xp, y=yp, method='linear', assume_sorted=True).T
    tsax.contourf(hp.age/1e3, hp.d, hp, alpha=0.75,
                  colors=[c], levels=[1.0, 5e3])

    # set axes properties
    tsax.set_xlim(120.0, 0.0)
    tsax.set_xlabel('model age (ka)')
    tsax.set_ylabel('glacier length (km)')
    tsax.xaxis.set_visible(i==len(regions)-1)
    tsax.yaxis.set_label_position("right")
    tsax.yaxis.tick_right()
    tsax.grid(axis='y')

# save
util.pl.savefig()
