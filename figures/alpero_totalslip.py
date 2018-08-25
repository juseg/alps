#!/usr/bin/env python2
# coding: utf-8

import util as ut
import xarray as xr

# initialize figure
# FIXME postprocess netcdf erosion timeseries
fig, ax, cax = ut.pl.subplots_cax()


# Map axes
# --------

# load aggregated data
with xr.open_dataset('../data/processed/alpero.1km.epic.pp.agg.nc',
                     decode_times=False) as ds:
    ext = ds.totalslip > 0.0
    tts = ds.totalslip.where(ext)/1e3

    # plot aggregated data
    ckw = dict(label='cumulative basal motion (km)', format='%.0f')
    tts.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Reds', levels=[10**(0.5*i) for i in range(4, 11)])
    ext.plot.contour(ax=ax, colors='k', linewidths=0.5, levels=[0.5])

    # add map elements
    ut.pl.draw_boot_topo(ax)
    ut.pl.draw_natural_earth(ax)


# Time series
# -----------

## load postprocessed data
#age, slidingflux = ut.io.load_postproc_txt(ut.alpcyc_bestrun, 'slidingflux')
#
## plot time series
#twax = tsax.twinx()
#twax.plot(age/1e3, slidingflux/1e3, c=ut.pl.palette['darkred'])
#twax.set_ylabel('sliding flux ($10^3\,km^3\,a^{-1}$)', color=ut.pl.palette['darkred'])
#twax.set_xlim(120.0, 0.0)
#twax.set_ylim(-1.0, 7.0)
#twax.locator_params(axis='y', nbins=6)

# save figure
ut.pl.savefig()
