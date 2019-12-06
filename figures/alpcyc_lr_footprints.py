#!/usr/bin/env python
# Copyright (c) 2016--2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps cycle low-resolution footprints."""

import cartopy.crs as ccrs
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 85), nrows=2, ncols=3, sharex=True, sharey=True,
        subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=1.5, right=1.5, bottom=1.5, top=6.0, hspace=1.5, wspace=1.5))
    for ax, label in zip(grid.flat, 'abcdef'):
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s)' % label, ax=ax)

    # for each record
    for i, rec in enumerate(util.alpcyc_records):
        label = util.alpcyc_clabels[i]
        color = util.alpcyc_colours[i]
        conf = util.alpcyc_configs[i]
        ax = grid[0, i//2]

        # add scaling domain and outline on top panel only
        util.geo.draw_model_domain(ax, extent='rhlobe')
        util.geo.draw_lgm_outline(ax, edgecolor='k')

        # set title
        ax.text(0.25+0.5*('pp' in conf), 1.05, label, color=color,
                fontweight='bold', ha='center', transform=ax.transAxes)

        # load extra output
        with pismx.open.dataset(
                '../data/processed/alpcyc.2km.{}.{}.agg.nc'.format(
                    rec.lower()[:4], ('cp', 'pp')['pp' in conf])) as dataset:

            # draw stage 2 and 4 footprints
            for ax, stage in zip(grid[:, i//2], ['2', '4']):
                dataset['mis{}print'.format(stage)].plot.contourf(
                    ax=ax, add_colorbar=False, alpha=0.75,
                    colors=[color], extend='neither', levels=[0.5, 1.5])
                util.com.add_corner_tag('MIS ' + stage, ax=ax, va='bottom')
                util.geo.draw_boot_topo(ax=ax, filename='alpcyc.2km.in.nc')
                util.geo.draw_natural_earth(ax)

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
