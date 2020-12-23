#!/usr/bin/env python
# Copyright (c) 2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion power laws from the literature."""

import numpy as np
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(85, 85), gridspec_kw=dict(
        left=12, right=1.5, bottom=9, top=1.5))

    # plot erosion laws (in mm/a)
    x = np.logspace(0, 4)
    ax.plot(x, 1.665e-1*x**0.6459, c='0.25', label='Cook et al., 2020')
    ax.plot(x, 2.7e-4*x**2.02, c='C11', label='Herman et al., 2015')
    ax.plot(x, 5.2e-8*x**2.34, c='C1', label='Koppes et al., 2015')
    ax.plot(x, 5.3e-9*x**2.62, c='C0', label='Koppes et al., 2015')

    # set axes properties
    ax.legend()
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'sliding velocity ($m\,a^{-1}$)')
    ax.set_ylabel(r'erosion rate ($mm\,a^{-1}$)')
    ax.set_xlim(10**-0.1, 10**4.1)
    ax.set_ylim(10**-2.1, 10**2.1)
    ax.grid()  # FIXME grids by default

    # prepare figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
