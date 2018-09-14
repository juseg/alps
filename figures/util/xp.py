# Copyright (c) 2018, Julien Seguinot <seguinot@vaw.baug.ethz.ch>

"""Styled plot from xarray data arrays or datasets."""

import util as ut
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def shaded_relief(darray, ax=None, dsl=0.0):
    """Plot shaded relief map from elevation data array."""

    # plot basal topography
    darray.plot.imshow(ax=ax, add_colorbar=False, cmap=ut.cm.topo,
                       vmin=-3e3, vmax=3e3, zorder=-1)
    darray.plot.contour(ax=ax, colors='#0978ab', levels=[0.0],
                        linestyles=['dashed'], linewidths=0.25)

    # add relief shading
    shades = ut.xr.multishading(darray)
    shades.plot.imshow(ax=ax, add_colorbar=False, cmap=ut.pl.shinemap,
                       vmin=-1.0, vmax=1.0, zorder=-1)
