# Copyright (c) 2018, Julien Seguinot <seguinot@vaw.baug.ethz.ch>

"""Figure creation and sublot helpers."""

# FIXME use absplots

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import cartopy.crs as ccrs
import util as ut

# Projections
# -----------

# geographic projections
utm = ccrs.UTM(32)

# geographic regions
regions = {'egu': (112.5e3, 1087.5e3, 4855e3, 5355e3),  # egu poster 975x500
           '1609': (120e3, 1080e3, 4835e3, 5375e3),     # alps 16:9 960x540
           'alps': (150e3, 1050e3, 4820e3, 5420e3),     # model domain 900x600
           'bern': (390e3, 465e3, 5125e3, 5175e3),      # Bern 75x50
           'crop': (155e3, 1045e3, 4825e3, 5415e3),     # 5 km crop 890x590
           'guil': (230e3, 470e3, 5050e3, 5240e3),      # Guillaume 240x190
           'west': (250e3, 700e3, 4970e3, 5270e3),      # western 450x300
           'inn':   (500e3, 815e3, 5125e3, 5350e3),     # Inn 315x225
           'isere': (230e3, 370e3, 5000e3, 5100e3),     # Isere 140x100
           'ivrea': (300e3, 440e3, 5000e3, 5100e3),     # Ivrea 140x100
           'rhine': (410e3, 620e3, 5150e3, 5300e3),     # Rhine 210x150
           'rhone': (300e3, 475e3, 5100e3, 5225e3),     # Rhone 175x125
           'rhlobe': (450e3, 600e3, 5225e3, 5325e3),    # Rhine lobe 150x100
           'taglia': (760e3, 865e3, 5105e3, 5180e3),    # Tagliamento 105x75
           'valais': (310e3, 460e3, 5065e3, 5165e3),    # Trimlines 150x100
           'aletsch': (414e3, 444e3, 5139e3, 5159e3),   # Aletsch 30x20
           'boulders': (190e3, 490e3, 5045e3, 5245e3)}  # Boulders 300x200 km


# Axes preparation
# ----------------

def add_subfig_label(text, ax=None, x=None, y=None, ha='left', va='top',
                     offset=2.5/25.4):
    """Add figure label in bold."""
    ax = ax or plt.gca()
    x = x or (ha == 'right')  # 0 for left edge, 1 for right edge
    y = y or (va == 'top')  # 0 for bottom edge, 1 for top edge
    xoffset = (1 - 2*x)*offset
    yoffset = (1 - 2*y)*offset
    offset = mtransforms.ScaledTranslation(
        xoffset, yoffset, ax.figure.dpi_scale_trans)
    return ax.text(x, y, text, ha=ha, va=va, fontweight='bold',
                   transform=ax.transAxes + offset)


def cut_ts_axes(ax, tsw=2/3., tsh=1/3.):
    """Cut timeseries inset into main axes."""
    fig = ax.figure
    pos = ax.get_position(original=True)  # cf mpl api changes 3.0.0
    figw, figh = fig.get_size_inches()*25.4
    ax.outline_patch.set_ec('none')
    x = [0.0, 1-tsw, 1-tsw, 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, tsh, tsh, 1.0, 1.0, 0.0]
    commkw = dict(clip_on=False, transform=ax.transAxes, zorder=3)
    polykw = dict(ec='k', fc='none', **commkw)
    rectkw = dict(ec='w', fc='w', **commkw)
    poly = plt.Polygon(list(zip(x, y)), **polykw)
    rect = plt.Rectangle((1-tsw, 0.0), tsw, tsh, **rectkw)
    tsax = fig.add_axes([pos.x1-tsw*(pos.x1-pos.x0)+12.0/figw, 9.0/figh,
                         tsw*(pos.x1-pos.x0)-24.0/figw,
                         tsh*(pos.y1-pos.y0)-15.0/figh])
    ax.add_patch(rect)
    ax.add_patch(poly)
    return tsax


def prepare_map_axes(ax, extent='alps'):
    """Prepare map axes before plotting."""
    ax.set_rasterization_zorder(2.5)
    ax.set_extent(regions[extent], crs=ax.projection)


def prepare_ts_axes(ax, dt=True, mis=True):
    """Prepare timeseries axes before plotting."""
    if dt is True:
        plot_dt(ax)
    if mis is True:
        plot_mis(ax)


# Single map subplot helpers
# --------------------------

def subplots_ts(nrows=1, ncols=1, sharex=True, sharey=False,
                mode='column', labels=True):
    """Init figure with margins adapted for simple timeseries."""
    figw, figh = (177.0, 85.0) if mode == 'page' else (85.0, 60.0)
    fig, grid = ut.mm.subplots_mm(nrows=nrows, ncols=ncols,
                                  sharex=sharex, sharey=sharey,
                                  figsize=(figw, figh),
                                  gridspec_kw=dict(left=12.0, right=1.5,
                                                   bottom=9.0, top=1.5,
                                                   hspace=1.5, wspace=1.5))
    if nrows*ncols > 1 and labels is True:
        for ax, l in zip(grid, list('abcdef')):
            add_subfig_label('({})'.format(l), ax=ax)
    return fig, grid


def subplots_cax(extent='alps'):
    """Init figure with unique subplot and colorbar inset."""
    figw, figh = 177.0, 119.0
    fig, ax = ut.mm.subplots_mm(figsize=(figw, figh), projection=utm,
                                gridspec_kw=dict(left=1.5, right=1.5,
                                                 bottom=1.5, top=1.5))
    cax = fig.add_axes([4.5/figw, 1-52.0/figh, 3.0/figw, 40.0/figh])
    prepare_map_axes(ax, extent=extent)
    return fig, ax, cax


def subplots_cax_ts(extent='alps', labels=True, dt=True, mis=True):
    """Init figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 177.0, 119.0
    fig, ax = ut.mm.subplots_mm(figsize=(figw, figh), projection=utm,
                                gridspec_kw=dict(left=1.5, right=1.5,
                                                 bottom=1.5, top=1.5))
    cax = fig.add_axes([4.5/figw, 1-50.5/figh, 3.0/figw, 40.0/figh])
    tsax = cut_ts_axes(ax)
    prepare_map_axes(ax, extent=extent)
    prepare_ts_axes(tsax, dt=dt, mis=mis)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax, tsax


def subplots_cax_ts_anim(extent='alps', labels=False, dt=True, mis=True):
    """Init figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 180.0, 120.0
    fig, ax = ut.mm.subplots_mm(figsize=(figw, figh), projection=utm,
                                gridspec_kw=dict(left=0.0, right=0.0,
                                                 bottom=0.0, top=0.0))
    cax = fig.add_axes([5.0/figw, 70.0/figh, 5.0/figw, 40.0/figh])
    tsax = fig.add_axes([75.0/figw, 10.0/figh, 90.0/figw, 22.5/figh])
    ax.outline_patch.set_ec('none')
    x = [1/3., 1/3., 1.0]
    y = [0.0, 1/3., 1/3.]
    line = plt.Line2D(x, y, color='k', clip_on=False,
                      transform=ax.transAxes, zorder=3)
    rect = plt.Rectangle((1/3., 0.0), 2/3., 1/3., ec='w', fc='w',
                         clip_on=False, transform=ax.transAxes, zorder=-1)
    tsax.add_line(line)
    tsax.add_patch(rect)
    prepare_map_axes(ax, extent=extent)
    prepare_ts_axes(tsax, dt=dt, mis=mis)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax, tsax


def subplots_cax_ts_egu(extent='egu', labels=False, dt=True, mis=True):
    """Init large figure with subplot, colorbar and timeseries insets."""
    figw, figh = 975.0, 500.0
    fig, ax = ut.mm.subplots_mm(figsize=(figw, figh), projection=utm,
                                gridspec_kw=dict(left=0.0, right=0.0,
                                                 bottom=0.0, top=0.0))
    cax1 = fig.add_axes([20.0/figw, 60.0/figh, 50.0/figw, 5.0/figh])
    cax2 = fig.add_axes([20.0/figw, 40.0/figh, 50.0/figw, 5.0/figh])
    ax.outline_patch.set_ec('none')
    prepare_map_axes(ax, extent=extent)
    tsax = None
    return fig, ax, cax1, cax2, tsax


def subplots_cax_ts_sgm(extent='alps', labels=False, dt=True, mis=True):
    """Init A3 figure with subplot, colorbar inset and timeseries cut."""
    figw, figh = 405.0, 271 + 1/3.
    fig, ax = ut.mm.subplots_mm(figsize=(figw, figh), projection=utm,
                                gridspec_kw=dict(left=2.5, right=2.5,
                                                 bottom=2.5, top=2.5))
    cax1 = fig.add_axes([12.5/figw, 1-32.5/figh, 50.0/figw, 5.0/figh])
    cax2 = fig.add_axes([12.5/figw, 1-52.5/figh, 50.0/figw, 5.0/figh])
    tsax = fig.add_axes([147.5/figw, 15.0/figh, 240.0/figw, 60.0/figh])
    ax.outline_patch.set_ec('none')
    xcut = 130.0/400.0  # ca. 1/3.
    ycut = 85.0/400.0*3/2  # ca. 1/3.
    x = [0.0, xcut, xcut, 1.0, 1.0, 0.0, 0.0]
    y = [0.0, 0.0, ycut, ycut, 1.0, 1.0, 0.0]
    poly = plt.Polygon(list(zip(x, y)), ec='k', fc='none', clip_on=False,
                       transform=ax.transAxes, zorder=3)
    rect = plt.Rectangle((xcut, 0.0), 1-xcut, ycut, ec='w', fc='w',
                         clip_on=False, transform=ax.transAxes, zorder=-1)
    tsax.add_patch(poly)
    tsax.add_patch(rect)
    prepare_map_axes(ax, extent=extent)
    prepare_ts_axes(tsax, dt=dt, mis=mis)
    if labels is True:
        add_subfig_label('(a)', ax=ax)
        add_subfig_label('(b)', ax=tsax)
    return fig, ax, cax1, cax2, tsax


# Multi map subplot helpers
# --------------------------

def subplots_6(extent='alps'):
    """Init figure with six subplot."""
    figw, figh = 177.0, 85.0
    fig, grid = ut.mm.subplots_mm(figsize=(figw, figh), projection=utm,
                                  nrows=2, ncols=3, sharex=True, sharey=True,
                                  gridspec_kw=dict(left=1.5, right=1.5,
                                                   bottom=1.5, top=6.0,
                                                   hspace=1.5, wspace=1.5))
    for ax, l in zip(grid.flat, 'abcdef'):
        prepare_map_axes(ax, extent=extent)
        add_subfig_label('(%s)' % l, ax=ax)
    return fig, grid


def subplots_inputs(extent='alps', mode='vertical'):

    # initialize figure
    figw, figh = 177.0, 142.5 if mode == 'horizontal' else 102.0
    fig = ut.mm.figure_mm(figsize=(figw, figh))

    # prepare two grids in horizontal mode
    if mode == 'horizontal':
        grid1 = fig.subplots_mm(nrows=1, ncols=3, squeeze=False,
                                gridspec_kw=dict(left=1.5, right=1.5,
                                                 bottom=103.0, top=1.5,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm))
        grid2 = fig.subplots_mm(nrows=2, ncols=3, squeeze=False,
                                gridspec_kw=dict(left=1.5, right=1.5,
                                                 bottom=12.0, top=53.0,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm))

    # prepare two grids in vertical mode
    else:
        grid1 = fig.subplots_mm(nrows=3, ncols=1, squeeze=False,
                                gridspec_kw=dict(left=1.5, right=127.5,
                                                 bottom=1.5, top=1.5,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm)).T
        grid2 = fig.subplots_mm(nrows=3, ncols=2, squeeze=False,
                                gridspec_kw=dict(left=64.5, right=15.0,
                                                 bottom=1.5, top=1.5,
                                                 wspace=1.5, hspace=1.5),
                                subplot_kw=dict(projection=utm)).T

    # merge axes grids
    grid = np.concatenate((grid1, grid2))

    # add colorbar axes
    for ax in grid[[0, 2], :].flat:
        pos = ax.get_position(original=True)  # cf mpl api changes 3.0.0
        if mode == 'horizontal':
            rect = [pos.x0, pos.y0-4.5/figh, pos.x1-pos.x0, 3.0/figh]
        else:
            rect = [pos.x1+1.5/figw, pos.y0, 3.0/figw, pos.y1-pos.y0]
        ax.cax = fig.add_axes(rect)

    # prepare axes
    for ax, l in zip(grid.flat, 'abcdfhegi'):
        prepare_map_axes(ax, extent=extent)
        add_subfig_label('(%s)' % l, ax=ax)

    # return figure and axes
    return fig, grid


def subplots_profiles(regions, labels):
    figw, figh = 177.0, 168.0
    nrows = len(regions)
    fig = ut.mm.figure_mm(figsize=(figw, figh))
    grid = fig.subplots_mm(nrows=nrows, ncols=1, sharex=False, sharey=False,
                           gridspec_kw=dict(left=1.5, right=figw-36.5,
                                            bottom=9.0, top=1.5,
                                            hspace=1.5, wspace=1.5),
                           subplot_kw=dict(projection=utm))
    tsgrid = fig.subplots_mm(nrows=nrows, ncols=1, sharex=True, sharey=False,
                             gridspec_kw=dict(left=38.0, right=12.0,
                                              bottom=9.0, top=1.5,
                                              hspace=1.5, wspace=1.5))
    for i, reg in enumerate(regions):
        ax = grid[i]
        tsax = tsgrid[i]
        prepare_map_axes(ax, extent=reg)
        plot_mis(tsax, y=(0.15 if i == nrows-1 else None))
        add_subfig_label('(%s)' % 'acegik'[i], ax=ax)
        add_subfig_label('(%s) ' % 'bdfhjl'[i] + labels[i], ax=tsax)
    return fig, grid, tsgrid


def subplots_trimlines(extent='valais', mode='column'):

    # initialize figure
    figw, figh = (177.0, 59.0) if mode == 'page' else (85.0, 115.0)
    fig = ut.mm.figure_mm(figsize=(figw, figh))

    # add axes in page mode
    if mode == 'page':
        ax = fig.add_axes([1.5/figw, 1.5/figh, 84.0/figw, 56.0/figh],
                          projection=utm)
        cax = fig.add_axes([12.0/figw, 53.0/figh, 30.0/figw, 3.0/figh])
        scax = fig.add_axes([103.0/figw, 9.0/figh, 48.5/figw, 48.5/figh])
        hsax = fig.add_axes([153.0/figw, 9.0/figh, 12.0/figw, 48.5/figh])

    # add axes in column mode
    else:
        ax = fig.add_axes([0.5/figw, 0.5/figh, 84.0/figw, 56.0/figh],
                          projection=utm)
        cax = fig.add_axes([12.0/figw, 52.0/figh, 30.0/figw, 3.0/figh])
        scax = fig.add_axes([11.75/figw, 65.5/figh, 48.0/figw, 48.0/figh])
        hsax = fig.add_axes([61.25/figw, 65.5/figh, 12.0/figw, 48.0/figh])

    # prepare map axes
    prepare_map_axes(ax, extent=extent)

    # add subfigure labels
    add_subfig_label('(a)', ax=scax)
    add_subfig_label('(b)', ax=hsax)
    add_subfig_label('(c)', ax=ax)

    # return figure and axes
    return fig, ax, cax, scax, hsax


# Timeseries elements
# -------------------

def plot_mis(ax=None, y=1.075):
    """Plot MIS stages."""
    # source: http://www.lorraine-lisiecki.com/LR04_MISboundaries.txt.

    # prepare blended transform
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)

    # add spans
    kwa = dict(fc='0.9', lw=0.25, zorder=0)
    ax.axvspan(71, 57, **kwa)
    ax.axvspan(29, 14, **kwa)

    # add text
    if y is not None:
        kwa = dict(ha='center', va='center', transform=trans)
        ax.text((120+71)/2, y, 'MIS 5', **kwa)
        ax.text((71+57)/2, y, 'MIS 4', **kwa)
        ax.text((57+29)/2, y, 'MIS 3', **kwa)
        ax.text((29+14)/2, y, 'MIS 2', **kwa)
        ax.text((14+0)/2, y, 'MIS 1', **kwa)


def plot_dt(ax=None, filename='alpcyc.2km.epic.pp.dt.nc'):
    """Plot scaled temperature offset time-series."""
    ax = ax or plt.gca()

    # plot time series
    with ut.io.open_dataset('../data/processed/'+filename) as ds:
        ax.plot(ds.age/1e3, ds.delta_T, c='0.25')

    # set axes properties
    ax.set_xlabel('model age (ka)')
    ax.set_ylabel('temperature offset (K)', color='0.25')
    ax.set_xlim(120.0, 0.0)
    ax.set_ylim(-17.5, 2.5)
    ax.grid(axis='y')
    ax.locator_params(axis='y', nbins=6)
