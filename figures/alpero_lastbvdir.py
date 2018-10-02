#!/usr/bin/env python
# coding: utf-8

import util as ut
import matplotlib.pyplot as plt

# initialize figure
fig, ax, cax = ut.fi.subplots_cax(extent='rhlobe')


# Map axes
# --------

# load aggregated data
with ut.io.open_dataset('../data/processed/alpero.1km.epic.pp.agg.nc') as ds:
    ext = ds.glerosion > 0.0
    bvm = ds.lastbvage.notnull()

    # plot
    norm = plt.Normalize(vmin=15.0, vmax=25.0)
    boolkw = dict(add_colorbar=False, levels=[0.5, 1.5], extend='neither')
    ss = ax.streamplot(ds.x, ds.y, ds.lastbvbvx.data, ds.lastbvbvy.data,
                       color=ds.lastbvage.data/1e3, cmap='Spectral', norm=norm,
                       density=(12, 8), linewidth=0.5, arrowsize=0.25)
    (ext^bvm).plot.contourf(ax=ax, alpha=0.0, hatches=['////'], **boolkw)
    ext.plot.contourf(ax=ax, alpha=0.75, colors='w', **boolkw)
    bvm.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.25,
                     linestyles=[(0, [3, 1])])
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.5)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.ne.draw_natural_earth(ax)

# add colorbar
cb = ut.pl.add_colorbar(ss.lines, cax, extend='both')
cb.set_label(r'age of deglaciation (ka)')

# save figure
ut.pl.savefig()
