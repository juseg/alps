#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# isotope stage bounds
agebounds = [[29, 14], [71, 57]]
idxbounds = [[909, 1059], [489, 629]]

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(170.0, 80.0), projection=ut.pl.utm,
                              nrows=2, ncols=3, sharex=True, sharey=True,
                              left=2.5, right=2.5, bottom=2.5, top=3.9,
                              hspace=2.5, wspace=2.5)

# add boot topo  # FIXME move to util
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-5km.nc')
for ax in grid.flat:
    ax.set_extent(ut.pl.regions['alps'], crs=ax.projection)
    ax.set_rasterization_zorder(2.5)
    im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    dt = ut.alpcyc_offsets[i]
    c = ut.alpcyc_colours[i]

    # set title
    if 'pp' not in conf:
        grid[0, i/2].set_title(rec, fontweight='bold', color=c)
        ut.pl.add_subfig_label('(%s)' % list('abc')[i/2], ax=grid[0, i/2])
        ut.pl.add_subfig_label('(%s)' % list('def')[i/2], ax=grid[1, i/2])

    # load extra output
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    nc = ut.io.load('output/e9d2d1f/alps-wcnn-5km/%s+%s/'
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
        ut.pl.draw_natural_earth(ax)
        ut.pl.draw_lgm_outline(ax, c='k')

# save
fig.savefig('alpcyc_lr_footprints')
