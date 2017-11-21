#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import iceplotlib.plot as iplt

# initialize figure
fig, grid, cax = ut.pl.subplots_6_cax()

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
    cmap = plt.get_cmap('Paired', 12)
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

# add colorbar
cb = ut.pl.add_colorbar(cs, cax)
cb.set_label(r'LGM age (ka)')

# save
ut.pl.savefig()
