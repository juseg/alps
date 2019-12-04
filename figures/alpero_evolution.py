#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion time evolution."""

import xarray as xr
import absplots as apl
import util


def figure():
    """Prepare initial animation figure."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(177, 119), gridspec_kw=dict(
        left=12, right=1.5, bottom=12, top=1.5))

    # load postprocessed data
    with xr.open_mfdataset([
            '../data/processed/alpero.1km.epic.pp.agg.nc',
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc'],
                           combine='by_coords', decode_cf=False,
                           join='override') as data:
        data = data[['slvol', 'erosion_rate']]
        data['time'] /= 365*24*60*60
        data['slvol'] *= 100
        data['erosion_rate'] *= 1e-9
        data['rolling_mean'] = data.erosion_rate.rolling(
            time=100, center=True).mean()

    # for volume changes use
    # slvol = slvol.rolling(time=100, center=True).mean()
    # slvol = slvol.differentiate('time')

    # plot
    line0, = ax.plot(data.slvol, data.erosion_rate, c='C11', alpha=0.5)
    line1, = ax.plot(data.slvol, data.rolling_mean, c='C11')
    timetag = ax.text(0.95, 0.95, '', ha='right', va='top',
                      transform=ax.transAxes)

    # set axes properties
    ax.set_xlabel('ice volume (cm s.l.e.)')
    ax.set_ylabel(r'erosion rate ($km^3\,a^{-1}$)')
    ax.set_yscale('log')
    ax.set_ylim(0.8e-2, 1.2e1)

    # return figure, data and animated artists
    return fig, data, line0, line1, timetag


def animate(time, data, line0, line1, timetag):
    """Update figure data."""

    # replace line data
    line0.set_ydata(data.erosion_rate.where(data.time <= time))
    line1.set_ydata(data.rolling_mean.where(data.time <= time))

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
    # import os
    # import sys
    # import matplotlib.animation as animation
    # ani = animation.FuncAnimation(
    #     fig, animate, blit=True, interval=1000/25, fargs=fargs,
    #     frames=range(-119000, 1, 40))
    # ani.save(os.path.splitext(sys.argv[0])[0] + '.mp4')


if __name__ == '__main__':
    main()
