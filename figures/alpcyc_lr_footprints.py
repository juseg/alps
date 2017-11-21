#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import iceplotlib.plot as iplt

# isotope stage bounds
agebounds = [[29, 14], [71, 57]]
idxbounds = [[909, 1059], [489, 629]]

# initialize figure
figw, figh = 175.0, 85.0
fig, grid = iplt.subplots_mm(figsize=(figw, figh), projection=ut.pl.utm,
                             nrows=2, ncols=3, sharex=True, sharey=True,
                             gridspec_kw=dict(left=2.5, right=2.5,
                                              bottom=2.5, top=20/3.,
                                              hspace=2.5, wspace=2.5))

# prepare axes
for ax in grid.flat:
    ax.set_extent(ut.pl.regions['alps'], crs=ax.projection)
    ax.set_rasterization_zorder(2.5)

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    dt = ut.alpcyc_offsets[i]
    c = ut.alpcyc_colours[i]
    ax = grid[0, i/2]
    pp = 'pp' in conf

    # add scaling domain and outline on top panel only
    ut.pl.draw_scaling_domain(ax)
    ut.pl.draw_lgm_outline(ax, c='k')

    # set title
    ax.text(0.4+0.1*pp, 1.05, label, color=c, fontweight='bold',
            ha=('left' if pp else 'right'), transform=ax.transAxes)

    # load extra output
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    nc = ut.io.load('output/e9d2d1f/alps-wcnn-2km/%s+%s/'
                    'y???????-extra.nc' % (dtfile, conf))
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
    thk = nc.variables['thk'][:]
    nc.close()

    # for each stage
    for j in range(2):
        ax = grid[j, i/2]
        b0, b1 = idxbounds[j]
        mask = (thk[b0:b1] < 1.0).prod(axis=0)
        cs = ax.contourf(x, y, mask, levels=[-0.5, 0.5], colors=[c], alpha=0.75)
        ut.pl.add_corner_tag('MIS %d' % (2+2*j), ax=ax, va='bottom')
        ut.pl.add_subfig_label('(%s)' % list('abcdef')[i/2+j], ax=ax)
        ut.pl.draw_boot_topo(ax, res='2km')
        ut.pl.draw_natural_earth(ax)

# save
ut.pl.savefig()
