#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
# FIXME postprocess netcdf erosion timeseries
fig, ax, cax = ut.fi.subplots_cax()


# Map axes
# --------

# load aggregated data
with ut.io.open_dataset('../data/processed/alpero.1km.epic.pp.agg.nc') as ds:
    ext = ds.glerosion > 0.0
    ero = ds.glerosion.where(ext)

    # plot aggregated data
    ckw = dict(label='total erosion (m)')
    ero.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Reds', levels=[10**i for i in range(-1, 4)])
    ext.plot.contour(ax=ax, colors='k', linewidths=0.5, levels=[0.5])

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)


# Time series
# -----------

## load postprocessed data
#age, erosionrate = ut.io.load_postproc_txt(ut.alpcyc_bestrun, 'erosionrate')
#
## plot time series
#twax = tsax.twinx()
#twax.plot(age/1e3, erosionrate, c='C5')
#twax.set_ylabel('erosion rate ($km^3\,a^{-1}$)', color='C5')
#twax.set_xlim(120.0, 0.0)
#twax.set_ylim(-0.5, 3.5)
#twax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
