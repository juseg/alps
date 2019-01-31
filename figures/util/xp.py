# Copyright (c) 2018, Julien Seguinot <seguinot@vaw.baug.ethz.ch>

"""Styled plot from xarray data arrays or datasets."""

import util as ut
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartowik.conventions as ccv


def ice_extent(darray, ax=None, ec='0.25', fc='none'):
    """Draw void or filled ice extent contour."""

    # plot a single contour
    if ec is not 'none':
        darray.plot.contour(ax=ax, colors=[ec], levels=[0.5], linewidths=0.25)
    if fc is not 'none':
        darray.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors=fc,
                             extend='neither', levels=[0.5, 1.5])


def topo_contours(darray, ax=None, ec='0.25'):
    """Plot surface topography contours."""

    # contour levels
    levels = range(0, 5000, 200)
    majors = [l for l in levels if l % 1000 == 0]
    minors = [l for l in levels if l % 1000 != 0]

    # plot contours
    darray.plot.contour(ax=ax, colors=[ec], levels=majors, linewidths=0.25)
    darray.plot.contour(ax=ax, colors=[ec], levels=minors, linewidths=0.1)


def shaded_relief(darray, ax=None, mode='co'):
    """Plot shaded relief map from elevation data array."""

    # plot basal topography
    if mode == 'bw':
        kwargs = dict(cmap='Greys', vmin=0, vmax=3000)
    elif mode == 'co':
        kwargs = dict(cmap=ccv.ELEVATIONAL, vmin=-4500, vmax=4500)
    darray.plot.imshow(ax=ax, add_colorbar=False, zorder=-1, **kwargs)

    # add relief shading
    # FIXME: add xarray/numpy-centric functions in cartowik?
    shades = ut.xr.multishading(darray)
    shades.plot.imshow(ax=ax, add_colorbar=False, cmap=ccv.SHINES,
                       vmin=-1.0, vmax=1.0, zorder=-1)

    # add coastline if data spans the zero
    if darray.min() * darray.max() < 0.0:
        colors = ('0.25' if mode == 'bw' else '#0978ab')
        darray.plot.contour(ax=ax, colors=colors, levels=[0.0],
                            linestyles=['dashed'], linewidths=0.25)


def streamplot(dataset, ax=None, **kwargs):
    """Plot surface velocity streamlines."""

    # get current axes if none provided
    ax = ax or plt.gca()

    # extract velocities
    icy = dataset.thk.fillna(0.0) >= 1.0
    uvel = dataset.uvelsurf.where(icy).values
    vvel = dataset.vvelsurf.where(icy).values
    vmag = (uvel**2+vvel**2)**0.5

    # try add streamplot, handle lack of ice cover
    # FIXME report this as a bug in matplotlib
    try:
        ax.streamplot(dataset.x, dataset.y, uvel, vvel, color=vmag,
                      cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3),
                      arrowsize=0.25, linewidth=0.5, **kwargs)
    except ValueError:
        pass
