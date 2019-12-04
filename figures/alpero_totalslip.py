#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
# FIXME postprocess netcdf erosion timeseries
fig, ax, cax = util.fig.subplots_cax()


# Map axes
# --------

# load aggregated data
with util.io.open_dataset('../data/processed/alpero.1km.epic.pp.agg.nc') as ds:
    ext = ds.totalslip > 0.0
    tts = ds.totalslip.where(ext)/1e3

    # plot aggregated data
    ckw = dict(label='cumulative basal motion (km)', format='%.0f')
    tts.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Reds', levels=[10**(0.5*i) for i in range(4, 11)])
    ext.plot.contour(ax=ax, colors='k', linewidths=0.5, levels=[0.5])

    # add map elements
    util.geo.draw_boot_topo(ax)
    util.geo.draw_natural_earth(ax)


# Time series
# -----------

## load postprocessed data
#age, slidingflux = util.io.load_postproc_txt(util.alpcyc_bestrun, 'slidingflux')
#
## plot time series
#twax = tsax.twinx()
#twax.plot(age/1e3, slidingflux/1e3, c='C5')
#twax.set_ylabel('sliding flux ($10^3\,km^3\,a^{-1}$)', color='C5')
#twax.set_xlim(120.0, 0.0)
#twax.set_ylim(-1.0, 7.0)
#twax.locator_params(axis='y', nbins=6)

# save figure
util.com.savefig()
