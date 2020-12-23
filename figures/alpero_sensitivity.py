#!/usr/bin/env python
# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion sensibility to climate scenario."""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 80), nrows=2, ncols=3, sharex=True, sharey=True,
        subplot_kw=dict(projection=ccrs.UTM(32)), gridspec_kw=dict(
            left=1.5, right=1.5, bottom=1, top=1.5, hspace=1.5, wspace=1.5))

    # for each record
    for i, rec in enumerate(util.alpcyc_records):
        label = util.alpcyc_clabels[i]
        conf = util.alpcyc_configs[i]
        ax = grid.T.flat[i]

        # prepare axes and add labels
        util.fig.prepare_map_axes(ax)
        util.fig.add_subfig_label('(%s) ' % 'abcdef'[i], ax=ax)
        util.com.add_corner_tag(label, ax=ax, va='bottom', y=(i == 5)*1/3)

        # load aggregated data
        with pismx.open.dataset(
                '../data/processed/alpero.2km.{}.{}.agg.nc'.format(
                    rec.lower()[:4], ('cp', 'pp')['pp' in conf])) as ds:

            # plot map data
            cset = ds.her2015_cumu.plot.contourf(
                ax=ax, cmap='YlOrBr', levels=[10**i for i in range(0, 5)],
                alpha=0.75, add_colorbar=False)
            ds.her2015_cumu.notnull().plot.contour(
                ax=ax, colors='k', linewidths=0.5, levels=[0.5])

        # add map elements
        util.geo.draw_boot_topo(ax=ax, filename='alpcyc.2km.in.nc')
        util.geo.draw_natural_earth(ax)

    # cut out white rectangle
    ax.spines['geo'].set_visible(False)
    x = [0.0, 1/3, 1/3, 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, 1/3, 1/3, 1.0, 1.0, 0.0]
    kwa = dict(clip_on=False, transform=ax.transAxes, zorder=3)
    ax.add_patch(plt.Rectangle((1/3, 0.0), 2/3, 1/3, ec='w', fc='w', **kwa))
    ax.add_patch(plt.Polygon(list(zip(x, y)), ec='k', fc='none', **kwa))

    # add colorbar
    cax = fig.add_axes_mm([57*2+19+1.5*4, 38/3-3, 57*2/3-1.5, 3])
    fig.colorbar(cset, cax=cax, label='erosion potential (m)', format='%g',
                 orientation='horizontal')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
