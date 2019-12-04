#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, ax, cax, tsax = util.fi.subplots_cax_ts(dt=False, mis=False)
tsax.set_rasterization_zorder(2.5)


# Map axes
# --------

# load aggregated data
with util.io.open_dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    tpg = ds.maxexttpg
    srf = ds.maxextsrf
    fpt = ds.footprint
    ext = ds.maxextthk.notnull()
    age = ds.maxexttpg.age
    btp = ds.maxextbtp
    bvn = (ds.maxextbvx**2 + ds.maxextbvy**2)**0.5

    # identify problematic areas
    bvc = bvn.where(btp < -1e-3)
    bvw = bvn.where(btp >= -1e-3)

    # plot
    ckw = dict(label='cold-based sliding ($m\,a^{-1}$)')
    tpg.plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                    vmin=0.0, vmax=3e3, zorder=-1)
    bvn.plot.imshow(ax=ax, add_colorbar=False, alpha=0.75, cmap='Reds',
                    norm=util.pl.velnorm,
                    vmin=util.pl.velnorm.vmin, vmax=util.pl.velnorm.vmax)
    bvc.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Blues', levels=[1e-1, 1e0, 1e1])
    btp.plot.contour(ax=ax, colors='k', levels=[-1e-3],
                     linewidths=0.25, linestyles=['-'], zorder=0)
    srf.plot.contour(ax=ax, colors='0.25', levels=util.pl.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors='0.25', levels=util.pl.utlevs, linewidths=0.25)
    ext.plot.contour(ax=ax, levels=[0.5], colors='k', linewidths=0.25)

# add vector elements
util.ne.draw_natural_earth(ax)
util.pl.add_corner_tag('%.2f ka' % (age/1e3), ax)


# Time series
# -----------

# plot scatter
tsax.set_yscale('log')
tsax.set_xscale('symlog', linthreshx=1e-12)
tsax.scatter(btp, bvc, marker='.', c='C1', alpha=0.1)
tsax.scatter(btp, bvw, marker='.', c='C5', alpha=0.1)
tsax.set_xlabel('basal temperature below freezing (K)')
tsax.set_ylabel('basal velocity ($m\,a^{-1}$)')

# save figure
util.pl.savefig()
