#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion time evolution."""

import numpy as np
import matplotlib.animation as animation
import absplots as apl
import pismx.open


def figure():
    """Prepare initial animation figure."""

    # initialize figure
    fig = apl.figure_mm(figsize=(192, 108))
    fig.subplots_mm(nrows=3, sharex=True, gridspec_kw=dict(
        left=18, right=146, bottom=12, top=6, hspace=3))
    fig.subplots_mm(gridspec_kw=dict(
        left=61, right=6, bottom=12, top=6))
    axes = fig.axes

    # load postprocessed data (note: there seem to be currently no way to merge
    # two dataset with slight errors using mfdataset)
    with pismx.open.dataset(
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc') as ds:
        with pismx.open.dataset(
                '../data/processed/alpero.1km.epic.pp.agg.nc') as agg:
            agg = agg.reindex_like(ds, method='nearest', tolerance=1e-9)
            ds = ds.merge(agg, compat='override')

        # plot lines on small panels
        lines = []
        thk = ds.volume_glacierized/ds.area_glacierized
        for i, y in enumerate([
                ds.kop2015_rate,
                ds.kop2015_rate/ds.area_glacierized*1e3,
                ds.hum1994_rate/ds.area_glacierized*1e4,
                ]):

            # variable-dependent properties
            color = '0.25' if i == 2 else 'C11'
            lines += axes[i].plot(
                ds.area_glacierized/1e9, y, c=color, alpha=0.5)
            lines += axes[i].plot(
                ds.area_glacierized/1e9,
                y.rolling(age=100, center=True).mean(), c=color)

        # plot lines on main panel
        lines += axes[3].plot(
            ds.slvol*100, ds.kop2015_rate, c='C11', alpha=0.5,
            label='intantaneous values')
        lines += axes[3].plot(
            ds.slvol*100, ds.kop2015_rate.rolling(age=100, center=True).mean(),
            c='C11', label='1000 years rolling mean')

    # set axes properties
    axes[2].set_xlabel(r'glacierized area ($10^3\,km^2$)')
    axes[3].set_xlabel('ice volume (cm s.l.e.)')
    axes[0].set_ylabel('annual erosion volume\n'+r'($m^3\,a^{-1}$)')
    axes[1].set_ylabel('mean erosion rate\n'+r'($mm\,a^{-1}$)')
    axes[2].set_ylabel('mean sliding speed\n'+r'($m\,a^{-1}$)')
    axes[3].set_ylabel(r'annual erosion volume ($m^3\,a^{-1}$)')
    axes[0].set_yscale('log')
    axes[1].set_yscale('log')
    axes[2].set_yscale('log')
    axes[3].set_yscale('log')
    axes[0].set_ylim(10**4.25, 10**7.75)
    axes[1].set_ylim(10**-3.25, 10**0.25)
    axes[2].set_ylim(10**0.92, 10**2.08)
    axes[3].set_ylim(10**4.25, 10**7.75)
    for ax in axes[:3]:
        ax.yaxis.set_label_coords(-0.3, 0.5)
    axes[3].legend(loc='lower right')

    # add various annotations
    ax = axes[3]
    labels = [

        # top right corner time tag
        ax.text(0.95, 0.95, '', ha='right', va='top', fontweight='bold',
                transform=ax.transAxes),

        # advance and retreat arrows
        ax.annotate('', xy=(25, 10**5.1), xytext=(5, 10**5.1), arrowprops=dict(
            arrowstyle='->', lw=1, connectionstyle='arc3,rad=0.25')),
        ax.annotate('', xy=(5, 10**6.7), xytext=(25, 10**6.7), arrowprops=dict(
            arrowstyle='->', lw=1, connectionstyle='arc3,rad=0.25')),
        ax.text(15, 10**4.6, 'advance', ha='center', va='center'),
        ax.text(15, 10**7.2, 'retreat', ha='center', va='center'),

        # maximum stages circles
        ax.plot(21, 10**5.8, marker='o', ms=60, mec='k', mfc='none')[0],
        ax.plot(28, 10**5.7, marker='o', ms=60, mec='k', mfc='none')[0],
        ax.text(21, 10**6.3, 'MIS 4', ha='center', va='center'),
        ax.text(28, 10**6.2, 'MIS 2', ha='center', va='center')]

    # return figure, data and animated artists
    return fig, *lines, *labels


def animate(age, *fargs):
    """Update figure data."""

    # separate lines and labels
    lines = fargs[:8]
    labels = fargs[8:]

    # replace line data
    idx = (120e3-age)/10 - 1
    print("plotting frame at {:.0f} years ago...".format(age))
    for line in lines:
        line.set_ydata(np.ma.array(
            data=np.ma.getdata(line.get_ydata()),
            mask=np.arange(12000) > idx))

    # replace text tag
    labels[0].set_text('{:,.0f} years ago'.format(age).replace(',', r'$\,$'))

    # fade-in labels as needed
    def fadein(age, midpoint, duration=2500):
        x = np.clip((age-midpoint)/duration, -1, 1)
        return 0.25*x**3 - 0.75*x + 0.5
    labels[1].arrow_patch.set_alpha(fadein(age, 40e3))  # advance arrow
    labels[2].arrow_patch.set_alpha(fadein(age, 40e3))  # retreat arrow
    labels[3].set_alpha(fadein(age, 40e3))  # advance text
    labels[4].set_alpha(fadein(age, 40e3))  # retreat text
    labels[5].set_alpha(fadein(age, 60e3))  # mis 4 marker
    labels[6].set_alpha(fadein(age, 20e3))  # mis 2 marker
    labels[7].set_alpha(fadein(age, 60e3))  # mis 4 text
    labels[8].set_alpha(fadein(age, 20e3))  # mis 2 text

    # return animated artists
    return *lines, *labels


def main():
    """Main program called during execution."""

    # prepare figure
    fig, *fargs = figure()
    fig.savefig(__file__[:-3])

    # prepare animation
    ani = animation.FuncAnimation(
         fig, animate, blit=True, interval=1000/25, fargs=fargs,
         frames=range(120000-40, -1, -40))
    ani.save(__file__[:-3] + '_main.mp4')


if __name__ == '__main__':
    main()
