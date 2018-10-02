#!/usr/bin/env python
# coding: utf-8

import util as ut

# initialize figure
fig, grid = ut.fi.subplots_6()

# for each record
for i, rec in enumerate(ut.alpcyc_records):
    label = ut.alpcyc_clabels[i]
    conf = ut.alpcyc_configs[i]
    pp = 'pp' if 'pp' in conf else 'cp'
    dt = ut.alpcyc_offsets[i]
    c = ut.alpcyc_colours[i]
    ax = grid[0, i//2]

    # add scaling domain and outline on top panel only
    ut.pl.draw_model_domain(ax, extent='rhlobe')
    ut.na.draw_lgm_outline(ax, c='k')

    # set title
    ax.text(0.4+0.1*(pp in conf), 1.05, label, color=c, fontweight='bold',
            ha=('left' if pp in conf else 'right'), transform=ax.transAxes)

    # load extra output
    filename = 'alpcyc.2km.{}.{}.agg.nc'.format(rec.lower()[:4], pp)
    with ut.io.open_dataset('../data/processed/'+filename) as ds:

        # for each stage
        for j, ax in enumerate(grid[:, i//2]):
            stage = 2*j+2
            fpt = ds['mis{:d}print'.format(stage)]
            fpt.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75,
                              colors=[c], extend='neither', levels=[0.5, 1.5])
            ut.pl.add_corner_tag('MIS %d' % (stage), ax=ax, va='bottom')
            ut.pl.add_corner_tag('MIS ' + str(stage), ax=ax, va='bottom')
            ut.pl.add_corner_tag('MIS {}'.format(stage), ax=ax, va='bottom')
            ut.pl.draw_boot_topo(ax=ax, filename='alpcyc.2km.in.nc')
            ut.ne.draw_natural_earth(ax)

# save
ut.pl.savefig()
