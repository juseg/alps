#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion time evolution."""

import absplots as apl
import pismx.open
import util


def figure():
    """Prepare initial animation figure."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(85, 80), gridspec_kw=dict(
        left=12, right=1.5, bottom=9, top=1.5))

    # load postprocessed data
    # FIXME there is a data gap after merge, add tolerance
    with pismx.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
        ds = ds[['slvol']]
    with pismx.open.dataset(
            '../data/processed/alpero.1km.epic.pp.agg.nc') as agg:
        ds['kop2015_rate'] = agg.kop2015_rate

    # unit conversion and rolling mean
    ds['slvol'] *= 100
    ds['rolling_mean'] = ds.kop2015_rate.rolling(age=100, center=True).mean()

    # plot
    line0, = ax.plot(ds.slvol, ds.kop2015_rate, c='C11', alpha=0.5)
    line1, = ax.plot(ds.slvol, ds.rolling_mean, c='C11')
    timetag = ax.text(0.95, 0.95, '', ha='right', va='top',
                      transform=ax.transAxes)

    # set axes properties
    ax.set_xlabel('ice volume (cm s.l.e.)')
    ax.set_ylabel(r'annual erosion volume ($m^3 a^{-1}$)')
    ax.set_yscale('log')
    ax.set_ylim(10**4.3, 10**7.7)

    # annotate advance and retreat
    ax.annotate('', xy=(5, 10**6.7), xytext=(25, 10**6.7), arrowprops=dict(
        arrowstyle='->', color='0.25', lw=1, connectionstyle='arc3,rad=0.25'))
    ax.annotate('', xy=(25, 10**5.1), xytext=(5, 10**5.1), arrowprops=dict(
        arrowstyle='->', color='0.25', lw=1, connectionstyle='arc3,rad=0.25'))
    ax.text(15, 10**4.6, 'advance', ha='center', va='center')
    ax.text(15, 10**7.2, 'retreat', ha='center', va='center')

    # annotat2 maximum stages
    ax.plot(21, 10**5.8, marker='o', ms=40, mec='0.25', mfc='none')
    ax.plot(28, 10**5.7, marker='o', ms=40, mec='0.25', mfc='none')
    ax.text(21, 10**6.3, 'MIS 4', ha='center', va='center')
    ax.text(28, 10**6.2, 'MIS 2', ha='center', va='center')

    # return figure, data and animated artists
    return fig, ds, line0, line1, timetag


def animate(time, ds, line0, line1, timetag):
    """Update figure data."""

    # replace line data
    line0.set_ydata(ds.kop2015_rate.where(ds.time <= time))
    line1.set_ydata(ds.rolling_mean.where(ds.time <= time))

    # replace text tag
    timetag.set_text('{:,.0f} years ago'.format(-time).replace(',', r'$\,$'))

    # return animated artists
    return line0, line1, timetag


def main():
    """Main program called during execution."""

    # prepare figure
    fig, *fargs = figure()
    util.com.savefig(fig)

    # prepare animation
    # FIXME prepare a fancy animation in separate script
    # import os
    # import sys
    # import matplotlib.animation as animation
    # ani = animation.FuncAnimation(
    #     fig, animate, blit=True, interval=1000/25, fargs=fargs,
    #     frames=range(-119000, 1, 40))
    # ani.save(os.path.splitext(sys.argv[0])[0] + '.mp4')


if __name__ == '__main__':
    main()
