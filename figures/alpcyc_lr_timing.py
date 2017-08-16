#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
# FIXME add colorbar
fig, grid = ut.pl.subplots_mm(figsize=(170.0, 80.0), projection=ut.pl.utm,
                              nrows=2, ncols=3, sharex=True, sharey=True,
                              left=2.5, right=2.5, bottom=2.5, top=3.9,
                              hspace=2.5, wspace=2.5)

# set extent
for i, ax in enumerate(grid.flat):
    ut.pl.add_subfig_label('(%s)' % list('abcdef')[i], ax=ax)
    ax.set_extent(ut.pl.regions['alps'], crs=ax.projection)
    ax.set_rasterization_zorder(2.5)

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    dt = ut.alpcyc_offsets[i]
    c = ut.alpcyc_colours[i]
    ax = grid[i%2, i/2]

    # set title
    if 'pp' not in conf:
        ax.set_title(rec, fontweight='bold', color=c)

    # load extra output
    dtfile = '%s3222cool%04d' % (rec.replace('-', '').lower(), round(dt*100))
    nc = ut.io.load('output/e9d2d1f/alps-wcnn-2km/%s+%s/'
                    'y???????-extra.nc' % (dtfile, conf))
    x = nc.variables['x'][:]
    y = nc.variables['y'][:]
    age = -nc.variables['time'][909:1059]/(1e3*365.0*24*60*60)
    thk = nc.variables['thk'][909:1059]
    usurf = nc.variables['usurf'][909:1059]

    # compute LGM age
    argmax = usurf.argmax(axis=0)
    lgmage = age[argmax]
    cols, rows = usurf.shape[1:]

    # apply thickness mask
    mask = (thk < 1.0).prod(axis=0)
    lgmage = np.ma.masked_where(mask, lgmage)

    # print bounds
    #print 'LGM age min %.1f, max %.1f' % (lgmage.min(), lgmage.max())

    # set contour levels, colors and hatches
    levs = range(19, 26)
    cmap = ut.pl.get_cmap('Paired', 12)
    cols = cmap(range(12))[:len(levs)+1]

    # plot
    cs = ax.contourf(x, y, lgmage, levs, colors=cols, extend='both', alpha=0.75)

    # ice margin
    ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.5)

    # close nc file
    nc.close()

    # add map elements
    ut.pl.add_corner_tag(label, ax=ax, va='bottom')
    ut.pl.draw_boot_topo(ax, res='2km')
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_lgm_outline(ax, c='k')

# save
fig.savefig('alpcyc_lr_timing')
