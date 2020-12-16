#!/usr/bin/env python
# Copyright (c) 2018-2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import matplotlib as mpl
import matplotlib.pyplot as plt
import absplots as apl

"""Plot Alps 4k animations color bar overlays."""


def colorbar(mode='er'):
    """Plot color bar overlay for given mode."""

    # initialize figure
    fig = apl.figure_mm(figsize=(24, 40))
    cax = fig.add_axes_mm([4, 4, 4, 32])

    # mode dependent properties
    if mode == 'er':
        levels = [10**i for i in range(-9, 1)]
        kwargs = dict(cmap='YlOrBr', label='erosion rate ($m\\,a^{-1}$)',
                      format=mpl.ticker.LogFormatterMathtext(),
                      ticks=levels[::3])  # (cax.locator_params issue #11937)
    elif mode == 'ul':
        levels = [-100, -50, -20, 0, 2, 5, 10]
        kwargs = dict(cmap='PRGn_r', label='uplift (m)')

    # add colorbar
    mpl.colorbar.ColorbarBase(
        ax=cax, alpha=0.75, boundaries=[levels[0]-1]+levels+[levels[-1]+1],
        extend='both', norm=mpl.colors.BoundaryNorm(levels, 256), **kwargs)

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['er', 'ul'])
    args = parser.parse_args()

    # set default font properties
    plt.rc('savefig', dpi=508, facecolor='none')
    plt.rc('axes', facecolor='none')

    # assemble overlay
    colorbar(args.mode).savefig(
        'anim_alps_4k_cbar_{}_en.png'.format(args.mode))


if __name__ == '__main__':
    main()
