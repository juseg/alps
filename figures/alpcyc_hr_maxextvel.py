#!/usr/bin/env python
# coding: utf-8

import hyoga.open
import util

# initialize figure
fig, ax, cax, tsax = util.fig.subplots_cax_ts()


# Map axes
# --------

# load aggregated data
with hyoga.open.dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    tpg = ds.maxexttpg
    srf = ds.maxextsrf
    fpt = ds.footprint
    ext = (ds.maxextthk.notnull())
    svn = (ds.maxextsvx**2 + ds.maxextsvy**2)**0.5
    age = ds.maxexttpg.age

    # plot
    ckw=dict(label=r'surface velocity ($m\,a^{-1}$)')
    tpg.plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                    vmin=0.0, vmax=3e3, zorder=-1)
    fpt.plot.contour(ax=ax, colors=['C7'], levels=[0.5],
                     linewidths=0.5, linestyles=[(0, [3, 1])])
    svn.plot.imshow(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                    cmap='Blues', norm=util.com.velnorm,  # (xarray issue 2381)
                    vmin=util.com.velnorm.vmin, vmax=util.com.velnorm.vmax)
    srf.plot.contour(ax=ax, colors=['0.25'], levels=util.com.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors=['0.25'], levels=util.com.utlevs,
                     linewidths=0.25)
    ext.plot.contour(ax=ax, levels=[0.5], colors='k', linewidths=0.25)

# add vector elements
util.geo.draw_natural_earth(ax)
util.geo.draw_lgm_outline(ax)
util.cyc.draw_glacier_names(ax)
util.cyc.draw_transfluences(ax)
util.com.add_corner_tag('%.2f ka' % (age/1e3), ax=ax)


# Time series
# -----------

# load time series
with hyoga.open.dataset('../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:

    # plot time series
    twax = tsax.twinx()
    twax.plot(ds.age, ds.slvol, c='C1')
    twax.set_ylabel('ice volume (m s.l.e.)', color='C1')
    twax.set_xlim(120.0, 0.0)
    twax.set_ylim(-0.05, 0.35)

# add cursor
cursor = tsax.axvline(age/1e3, c='k', lw=0.25)

# save figure
util.com.savefig()
