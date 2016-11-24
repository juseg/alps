#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# parameters
records = ['epica']
configs = ['', '+esia5']
offsets = np.arange(9.0, 10.1, 0.1)
colmaps = ['Reds', 'Blues']

# initialize figure
figw, figh = 85.0, 87.5
fig, grid = ut.pl.subplots_mm(figsize=(figw, figh), projection=ut.pl.utm,
                              nrows=2, ncols=1, sharex=True, sharey=True,
                              left=2.5, right=22.5, bottom=2.5, top=2.5,
                              hspace=2.5, wspace=2.5)
cax = fig.add_axes([1-20.0/figw, 2.5/figh, 5.0/figw, 82.5/figh])
for ax in grid.flat:
    ax.set_rasterization_zorder(2.5)

# for each record
for i, rec in enumerate(records):
    cmap = colmaps[i]

    # for each config
    for j, conf in enumerate(configs):
        ax = grid[j]
        footprints = []

        # draw boot topo
        nc = ut.io.load('input/boot/alps-srtm-5km.nc')
        im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
        nc.close()

        # draw lgm
        ut.pl.draw_lgm_outline(ax)
    
        # loop on offsets
        for dt in offsets:

            # load extra file
            nc = ut.io.load('output/0.7.3/alps-wcnn-5km/'
                            '%s3222cool%04d+acyc1%s/y0120000-extra.nc'
                            % (rec, round(dt*100), conf))
            x = nc.variables['x'][:]
            y = nc.variables['y'][:]
            thk = nc.variables['thk'][:]
            nc.close()

            # compute footprint
            footprints.append(1 - (thk < 1.0).prod(axis=0))

        # compute cooling required to cover each grid cell
        footprints = np.array(footprints)
        isglac = footprints.any(axis=0)
        dtglac = np.where(isglac, offsets[footprints.argmax(axis=0)], 99)

        # plot
        cs = ax.contour(x, y, isglac.T, linewidths=0.5, colors='k')
        cs = ax.contour(x, y, dtglac.T, offsets, linewidths=0.25, colors='k')
        cs = ax.contourf(x, y, dtglac.T, offsets, cmap=cmap, extend='min', alpha=0.75)

        # add label
        esia = {'': 2, '+esia5': 5}[conf]
        label = rec.upper() + ', $E_{SIA} = %d$' % esia
        ax.text(0.95, 0.05, label, transform=ax.transAxes, ha='right')

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'temperature offset (K)')

# save
fig.savefig('footprints')
