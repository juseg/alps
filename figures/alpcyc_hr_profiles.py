#!/usr/bin/env python2
# coding: utf-8

import util as ut
import matplotlib.pyplot as plt

# parameters
regions = ['rhine', 'rhone', 'ivrea', 'isere', 'inn', 'taglia']
labels = ['Rhine', 'Rhone', 'Dora Baltea', u'Isère', 'Inn', 'Tagliamento']

# initialize figure
fig, grid, tsgrid = ut.pl.subplots_profiles(regions, labels)

# load extra data in memory (interp on dask array takes 12min per profile)
with ut.io.load_mfoutput(ut.alpcyc_bestrun+'y???????-extra.nc') as ds:
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
    with ut.io.load_postproc('alpcyc.1km.epic.pp.agg.nc') as ds:
        srf = ds.maxthksrf
        ext = ds.maxthksrf.notnull()

        # plot surface contours and footprint
        ext.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors='w',
                          extend='neither', levels=[0.5, 1.5])
        ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.25)

    # remove title from xarray
    ax.set_title('')

    # add map elements
    ut.pl.draw_boot_topo(ax)
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_lgm_outline(ax)

    # add profile line from shapefile
    xp, yp = ut.io.open_shp_coords('profile_'+reg+'.shp')
    ax.plot(xp, yp, c=c, dashes=(2, 1))
    ax.plot(xp[0], yp[0], c=c, marker='o')


    # Time series
    # -----------

    # interpolate thickness and plot envelope
    hp = thk.interp(x=xp, y=yp, method='linear', assume_sorted=True).T
    hp.plot.contourf(ax=tsax, alpha=0.75, add_colorbar=False,
                     colors=[c], extend='neither', levels=[1.0, 5e3])

    # set axes properties
    tsax.set_xlim(120.0, 0.0)
    tsax.set_xlabel('model age (ka)')
    tsax.set_ylabel('glacier length (km)')
    tsax.xaxis.set_visible(i==len(regions)-1)
    tsax.yaxis.set_label_position("right")
    tsax.yaxis.tick_right()
    tsax.grid(axis='y')

# save
ut.pl.savefig()
