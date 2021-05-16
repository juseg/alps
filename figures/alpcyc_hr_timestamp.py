#!/usr/bin/env python
# Copyright (c) 2015-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Alps cycle hi-res computing time stamps."""

import hyoga.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = util.fig.subplots_ts()

    # plot cumulative time stamp
    with hyoga.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.tms.nc') as ds:
        diff = ds.timestamp.diff('age')
        procs = 576  # ds['rank'].max() + 1
        stamp = diff.where(diff > 0, ds.timestamp[1:]).cumsum()
        stamp.plot(ax=ax, color='C1', label=r'{:d} cores, {:.0f} kch'.format(
            int(procs), float(procs*stamp[-1]/1e3)))

    # set axes properies
    ax.invert_xaxis()
    ax.set_xlabel('model age (ka)')
    ax.set_ylabel('computing time (hours)')
    ax.legend(loc='best')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
