# Copyright (c) 2016--2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Alps project common tools.
"""

import os
import sys
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.collections as mcollections
import util as ut

# Color palette
# -------------

# set color cycle to colorbrewer Paired palette
plt.rc('axes', prop_cycle=plt.cycler(color=plt.get_cmap('Paired').colors))


# Mapping properties
# ------------------

# velocity norm
velnorm = mcolors.LogNorm(1e1, 1e3)

# contour levels
topolevs = range(0, 5000, 200)
inlevs = [l for l in topolevs if l % 1000 != 0]
utlevs = [l for l in topolevs if l % 1000 == 0]


# Convert between coords and extent
# ---------------------------------


def extent_from_coords(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n


# Text annotations
# ----------------

def add_colorbar(mappable, cax=None, ax=None, fig=None, label=None, **kw):
    """Add colorbar with auto orientation."""

    # try to figure out orientation
    orientation = kw.pop('orientation', None)
    if orientation is None and cax is not None:
        fig = cax.figure
        pos = cax.get_position().transformed(fig.dpi_scale_trans.inverted())
        ratio = abs(pos.height/pos.width)
        orientation = 'horizontal' if ratio < 1.0 else 'vertical'

    # find figure
    if fig is None:
        if cax is not None:
            fig = cax.figure
        elif ax is not None:
            fig = ax.figure
        else:
            fig = plt.gcf()

    # add colorbar
    cb = fig.colorbar(mappable, cax, orientation=orientation, **kw)

    # return colorbar
    return cb


def add_corner_tag(text, ax=None, ha='right', va='top', offset=2.5/25.4):
    """Add text in figure corner."""
    return ut.fig.add_subfig_label(text, ax=ax, ha=ha, va=va, offset=offset)


def add_signature(text, fig=None, offset=2.5/25.4):
    """Add signature for animations."""
    fig = fig or plt.gcf()
    figw, figh = fig.get_size_inches()
    fig.text(1-offset/figw, offset/figh, text, ha='right', va='bottom')


# Map elements
# ------------


# Saving figures
# --------------

def savefig(fig=None):
    """Save figure to script filename."""
    fig = fig or plt.gcf()
    res = fig.savefig(os.path.splitext(sys.argv[0])[0])
    return res
