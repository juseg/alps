#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(170.0, 80.0), projection=ut.pl.utm,
                              nrows=2, ncols=3, sharex=True, sharey=True,
                              left=2.5, right=2.5, bottom=2.5, top=3.9,
                              hspace=2.5, wspace=2.5)
w, e, s, n = ut.pl.regions['rhlobe']

# add boot topo  # FIXME move to util
nc = ut.io.load('input/boot/alps-srtmsub+gou11simi-5km.nc')
for i, ax in enumerate(grid.flat):
    ut.pl.add_subfig_label('(%s)' % list('abcdef')[i], ax=ax)
    ax.set_extent(ut.pl.regions['alps'], crs=ax.projection)
    ax.set_rasterization_zorder(2.5)
    im = nc.imshow('topg', ax=ax, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
nc.close()

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    cmap = ut.alpcyc_colmaps[i]
    pick = ut.alpcyc_offsets[i]
    c = ut.alpcyc_colours[i]
    ax = grid[i%2, i/2]
    stackprint = np.nan

    # set title
    if 'pp' not in conf:
        ax.set_title(rec, fontweight='bold', color=c)

    # loop on offsets
    for dt in np.arange(14.0, 5.9, -0.1):

        # try to find max area
        try:

            # load extra file
            dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
            nc = ut.io.load('output/e9d2d1f/alps-wcnn-5km/%s+%s/'
                            'y0120000-extra.nc' % (dtfile, conf))
            x = nc.variables['x'][:]
            y = nc.variables['y'][:]
            thk = nc.variables['thk'][909:1059, :, :]  # 29 to 14 ka
            nc.close()

            # compute footprint
            footprint = 1 - (thk < 1.0).prod(axis=0)
            stackprint = np.where(footprint, dt, stackprint)
            #ax.set_extent(ut.pl.regions['rhlobe'], crs=ax.projection)

            # plot contour
            lw = (0.25 if abs(dt - pick) < 1e-12 else 0.1)
            cs = ax.contour(x, y, footprint, levels=[0.5],
                            colors=['k'], linewidths=lw)

        # else do nothing
        except (RuntimeError, IndexError):
            pass

    # continue if no files found
    if stackprint is np.nan:
        continue

    # plot
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    n = (3*y[0]-y[1])/2
    s = (3*y[-1]-y[-2])/2
    im = ax.imshow(stackprint, extent=(w, e, n, s), cmap=cmap, alpha=0.75)

    # add map elements
    ut.pl.add_corner_tag(label, ax=ax, va='bottom')
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_lgm_outline(ax, c='k')

# save
fig.savefig('alpcyc_lr_stackprints')
