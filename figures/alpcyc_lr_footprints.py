#!/usr/bin/env python
# coding: utf-8

import util

# initialize figure
fig, grid = util.fi.subplots_6()

# for each record
for i, rec in enumerate(util.alpcyc_records):
    label = util.alpcyc_clabels[i]
    conf = util.alpcyc_configs[i]
    pp = 'pp' if 'pp' in conf else 'cp'
    dt = util.alpcyc_offsets[i]
    c = util.alpcyc_colours[i]
    ax = grid[0, i//2]

    # add scaling domain and outline on top panel only
    util.pl.draw_model_domain(ax, extent='rhlobe')
    util.geo.draw_lgm_outline(ax, edgecolor='k')

    # set title
    ax.text(0.4+0.1*(pp in conf), 1.05, label, color=c, fontweight='bold',
            ha=('left' if pp in conf else 'right'), transform=ax.transAxes)

    # load extra output
    filename = 'alpcyc.2km.{}.{}.agg.nc'.format(rec.lower()[:4], pp)
    with util.io.open_dataset('../data/processed/'+filename) as ds:

        # for each stage
        for j, ax in enumerate(grid[:, i//2]):
            stage = 2*j+2
            fpt = ds['mis{:d}print'.format(stage)]
            fpt.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75,
                              colors=[c], extend='neither', levels=[0.5, 1.5])
            util.pl.add_corner_tag('MIS %d' % (stage), ax=ax, va='bottom')
            util.pl.add_corner_tag('MIS ' + str(stage), ax=ax, va='bottom')
            util.pl.add_corner_tag('MIS {}'.format(stage), ax=ax, va='bottom')
            util.pl.draw_boot_topo(ax=ax, filename='alpcyc.2km.in.nc')
            util.geo.draw_natural_earth(ax)

# save
util.pl.savefig()
