#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
# FIXME: refine offsets
records = ['GRIP', 'EPICA', 'MD01-2444']
configs = ['+esia5', '+esia5', '+esia5']
offsets = [8.0, 9.5, 8.0]
colors = ['darkblue', 'darkred', 'darkgreen']
colors = [ut.pl.palette[c] for c in colors]

# isotope stage bounds
agebounds = [[71, 57], [29, 14]]
idxbounds = [[489, 629], [909, 1059]]

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(170.0, 80.0), projection=ut.pl.utm,
                              nrows=2, ncols=3, sharex=True, sharey=True,
                              left=2.5, right=2.5, bottom=2.5, top=5.0,
                              hspace=2.5, wspace=2.5)

# add boot topo
nc = ut.io.load('input/boot/alps-srtm-5km.nc')
for ax in grid.flat:
    ax.set_rasterization_zorder(2.5)
    im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# for each record
for i, rec in enumerate(records):
    conf = configs[i]
    dt = offsets[i]
    c = colors[i]

    # set title
    grid[0, i].set_title(rec, fontweight='bold', color=c)

    # load extra output
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    nc = ut.io.load('output/0.7.3/alps-wcnn-5km/%s+acyc1%s/y0120000-extra.nc'
                    % (dtfile, conf))
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
    thk = nc.variables['thk'][:]
    nc.close()

    # for each stage
    for j in range(2):
        ax = grid[j, i]
        b0, b1 = idxbounds[j]
        mask = (thk[b0:b1] < 1.0).prod(axis=0)
        cs = ax.contourf(x, y, mask.T, levels=[-0.5, 0.5], colors=[c], alpha=0.75)
        ut.pl.add_corner_tag('MIS %d' % (4-2*j), ax=ax, va='bottom')
        ut.pl.add_subfig_label('(%s)' % list('abcdef')[i+3*j], ax=ax)
        ut.pl.draw_natural_earth(ax)

# save
fig.savefig('footprints')
