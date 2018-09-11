#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(dt=False, mis=False)


# Map axes
# --------

# load aggregated data
with ut.io.load_postproc('alpcyc.1km.epic.pp.agg.nc') as ds:
    tpg = ds.maxexttpg
    srf = ds.maxextsrf
    ext = ds.maxextthk.notnull()
    age = ds.maxexttpg.age
    dvx = ds.maxextsvx - ds.maxextbvx
    dvy = ds.maxextsvy - ds.maxextbvy
    dvn = (dvx**2 + dvy**2)**0.5

    # plot
    ckw=dict(label=r'deformation velocity ($m\,a^{-1}$)')
    tpg.plot.imshow(ax=ax, add_colorbar=False, cmap='Greys',
                    vmin=0.0, vmax=3e3, zorder=-1)
    dvn.plot.contourf(ax=ax, alpha=0.75, cbar_ax=cax, cbar_kwargs=ckw,
                      cmap='Blues', levels=[1e0, 1e1, 1e2])
    srf.plot.contour(ax=ax, colors='0.25', levels=ut.pl.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors='0.25', levels=ut.pl.utlevs, linewidths=0.25)
    ext.plot.contour(ax=ax, levels=[0.5], colors='k', linewidths=0.25)

# add vector elements
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.add_corner_tag('%.2f ka' % (age/1e3), ax)


# Histograms
# ----------

# plot histograms
bins = [0.0] + [10**i for i in range(-8, 5)]
dvn.plot.hist(ax=tsax, bins=bins, color='C1', alpha=0.75)

# set axes properties
tsax.set_xscale('symlog', linthreshx=1e-8, linscalex=1.0)
tsax.set_yscale('log')
tsax.set_xlabel('deformation velocity ($m\,a^{-1}$)')
tsax.set_ylabel('grid cells')
tsax.set_title('')

# save figure
ut.pl.savefig()
