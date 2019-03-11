# Copyright (c) 2018, Julien Seguinot <seguinot@vaw.baug.ethz.ch>

"""Animation tools."""

import os
import re
import numpy as np
from scipy import ndimage
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.io.shapereader as cshp
import cartowik.conventions as ccv
import cartowik.naturalearth as cne


# Figure creation
# ---------------

def axes_anim_dynamic(crop, t, t0=-120e3, t1=-0e3, figsize=(192.0, 108.0)):
    """Init dynamic extent figure and subplot."""

    # predefined crop regions
    regions = dict(
        al_0=(120e3, 1080e3, 4835e3, 5375e3),  # Alps   16:9  960x540 250m@4k
        al_1=(120e3, 1080e3, 4835e3, 5375e3),  # "
        lu_0=(416e3,  512e3, 5200e3, 5254e3),  # Luzern 16:9   96x54   25m@4k
        lu_1=(392e3,  520e3, 5196e3, 5268e3),  # Luzern 16:9  128x72   33m@4k
        ma_0=(234e3,  426e3, 4871e3, 4979e3),  # Marit. 16:9  192x108  50m@4k
        ma_1=(141e3,  429e3, 4829e3, 4991e3),  # Marit. 16:9  288x162  75m@4k
        ch_0=(380e3,  476e3, 5120e3, 5174e3),  # Switz. 16:9   96x54   25m@4k
        ch_1=(252e3,  636e3, 5072e3, 5288e3),  # Switz. 16:9  384x216 100m@4k
        zo_0=(329e3,  521e3, 5096e3, 5204e3),  # Switz. 16:9  192x108  50m@4k
        zo_1=(120e3, 1080e3, 4835e3, 5375e3),  # Alps   16:9  960x540 250m@4k
    )

    # init figure with full-frame axes
    figw, figh = figsize
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.UTM(32))
    ax.background_patch.set_fc('none')
    ax.outline_patch.set_ec('none')
    ax.set_rasterization_zorder(2.5)

    # compute dynamic extent
    e0, e1 = ('{}_{:d}'.format(crop, i) for i in (0, 1))
    zoom = 1.0*(t-t0)/(t1-t0)  # linear increase between 0 and 1
    zoom = zoom**2*(3-2*zoom)  # smooth zoom factor between 0 and 1
    extent = [c0 + (c1-c0)*zoom for (c0, c1) in zip(regions[e0], regions[e1])]

    # set dynamic extent, return fig and axes
    ax.set_extent(extent, crs=ax.projection)
    return fig, ax


def coords_from_axes(ax):
    """Compute coordinate vectors from matplotlib axes."""
    return coords_from_extent(ax.get_extent(),
                              *ax.figure.get_size_inches()*ax.figure.dpi)

def coords_from_extent(extent, cols, rows):
    """Compute coordinate vectors from image extent."""

    # compute dx and dy
    (w, e, s, n) = extent
    dx = (e-w) / cols
    dy = (n-s) / rows

    # prepare coordinate vectors
    xwcol = w + 0.5*dx  # x-coord of W row cell centers
    ysrow = s + 0.5*dy  # y-coord of N row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow + np.arange(rows)*dy  # from S to N

    # return coordinate vectors
    return x, y


# Map elements
# ------------

def draw_lgm_outline(ax=None, c='#e31a1c', alpha=0.75):
    """Add Ehlers et al. hole-filled LGM outline."""
    ax = ax or plt.gca()
    shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
    ax.add_geometries(shp.geometries(), ccrs.PlateCarree(), lw=0.5,
                      alpha=alpha, edgecolor=c, facecolor='none')
    del shp


def draw_lgm_faded(t, alpha=0.75, **kwargs):
    """Add LGM outline with fade-in and fade-out effects."""
    tred = (t+25000) / 5000
    fade = tred**4 - 2*tred**2 + 1
    if abs(tred) < 1:
        draw_lgm_outline(alpha=alpha*fade, **kwargs)


def draw_major_cities(ax=None, exclude=None, include=None, maxrank=5,
                      textoffset=2, lang='en'):
    """Add major city locations with names."""
    ax = ax or plt.gca()

    # get axes extent
    west, east, south, north = ax.get_extent()

    # relative label positions
    xloc = 'r'  # ('l' if xc < center[0] else 'r')
    yloc = 'u'  # ('l' if yc < center[1] else 'u')
    dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*textoffset
    dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*textoffset
    ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
    va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]

    # open shapefile data
    shp = cshp.Reader(cshp.natural_earth(
        resolution='10m', category='cultural', name='populated_places'))

    # loop on records
    for rec in shp.records():
        name = rec.attributes['name_'+lang]
        rank = rec.attributes['SCALERANK']

        # check rank and name
        if rank > maxrank and name not in include or name in exclude:
            continue

        # check location
        geom = rec.geometry
        crs = ccrs.PlateCarree()
        x, y = ax.projection.transform_point(geom.x, geom.y, src_crs=crs)
        if west > x or x > east or south > y or y > north:
            continue

        # plot
        ax.plot(x, y, marker='o', color='0.25', ms=2)
        ax.annotate(name, xy=(x, y), xytext=(dx, dy), color='0.25',
                    textcoords='offset points', ha=ha, va=va, clip_on=True)


def draw_natural_earth(ax=None, mode='gs', **kwargs):
    """Add Natural Earth geographic data vectors."""
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.95' if mode == 'gs' else '#c6ecff'
    cne.add_rivers(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)
    cne.add_lakes(ax=ax, edgecolor=edgecolor, facecolor=facecolor, zorder=0, **kwargs)
    cne.add_coastline(ax=ax, edgecolor=edgecolor, zorder=0, **kwargs)


def draw_swisstopo_hydrology(ax=None, mode='gs', **kwargs):

    swissplus = ccrs.TransverseMercator(
        central_longitude=7.439583333333333,
        central_latitude=46.95240555555556,
        false_easting=2600e3, false_northing=1200e3)

    # get axes if None provided
    ax = ax or plt.gca()
    edgecolor = '0.25' if mode == 'gs' else '#0978ab'
    facecolor = '0.85' if mode == 'gs' else '#c6ecff'

    # draw swisstopo rivers
    filename = '../data/external/25_DKM500_GEWAESSER_LIN.shp'
    shp = cshp.Reader(filename)
    for rec in shp.records():
        symb = rec.attributes['Symbol']
        geom = rec.geometry
        if symb != '':
            lw = 2.5*float(re.sub(r'[^0-9\.]', '', symb))
            ax.add_geometries(geom, swissplus, edgecolor=edgecolor,
                              facecolor='none', lw=lw, zorder=0, **kwargs)

    # draw swisstopo lakes
    filename = '../data/external/22_DKM500_GEWAESSER_PLY.shp'
    shp = cshp.Reader(filename)
    ax.add_geometries(shp.geometries(), swissplus, edgecolor=edgecolor,
                      facecolor=facecolor, lw=lw, zorder=0, **kwargs)


def draw_tailored_hydrology(ax=None, **kwargs):

    # get the current window extent
    ax = ax or plt.gca()
    w, e, s, n = ax.get_extent()

    # the reference region containing swisstopo data
    w0, e0, s0, n0 = 252e3,  636e3, 5072e3, 5288e3  # FIXME ch1 unprecise

    # compute intersection and fraction covered by data
    xoverlap = max(0, min(e, e0)-max(w, w0))
    yoverlap = max(0, min(n, n0)-max(s, s0))
    axesarea = (e-w) * (n-s)
    coverage = xoverlap * yoverlap / axesarea

    # compute layer transparencies
    alpha = (coverage-0.9) / 0.1       # linear increase from 0.9 to 1.0
    alpha = max(0.0, min(1.0, alpha))  # capped between 0 and 1
    alpha = alpha**2*(3-2*alpha)       # smooth transition between 0 and 1

    # plot one or both hydrology layers
    if coverage > 0.9:
        draw_swisstopo_hydrology(alpha=alpha, **kwargs)
    if coverage < 1.0:
        draw_natural_earth(alpha=1-alpha, **kwargs)


# Data input methods
# ------------------

def open_dataset(filename):
    """Open single-file dataset with age coordinate."""
    ds = xr.open_dataset(filename, decode_cf=False)
    if 'time' in ds.coords and 'seconds' in ds.time.units:
        ds = ds.assign_coords(time=ds.time/(365*24*60*60))
    if 'time' in ds.coords:
        ds = ds.assign_coords(age=-ds.time)
    return ds


def open_sealevel(t):
    ds = pd.read_csv('../data/external/spratt2016.txt', comment='#',
                     delimiter='\t', index_col='age_calkaBP').to_xarray()
    ds = ds.SeaLev_shortPC1.dropna('age_calkaBP')
    ds = min(ds.interp(age_calkaBP=-t/1e3, method='cubic').values, 0.0)
    return ds


def open_subdataset(filename, t, shift=120000, step=500):
    """Open subdataset in multi-file based on format string."""
    ds = open_dataset(filename.format(shift + t + (-t) % step))
    ds = ds.sel(time=t, method='nearest', tolerance=1e-6)
    return ds


def open_visual(filename, t, x, y, sigma=10000):
    """Load interpolated output for visualization."""

    # load SRTM bedrock topography
    with open_dataset('../data/external/srtm.nc') as ds:
        srtm = ds.usurf.fillna(0.0) - ds.thk.fillna(0.0)

    # try to smooth integer-precision steps
    if sigma > 0:
        dx = (x[-1]-x[0])/(len(x)-1)
        dy = (y[-1]-y[0])/(len(y)-1)
        assert abs(dy-dx) < 1e12
        filt = ndimage.gaussian_filter(srtm, sigma=sigma/dx)
        srtm += np.clip(filt-srtm, -1.0, 1.0)

    # load boot topo
    with open_dataset('../data/processed/alpcyc.1km.in.nc') as ds:
        boot = ds.topg

    # load extra data
    with open_subdataset(filename, t) as ds:
        ds = ds[['thk', 'topg', 'usurf', 'velsurf_mag']]

        # compute ice mask and bedrock uplift
        ds['icy'] = 1.0 * (ds.thk >= 1.0)
        ds['uplift'] = ds.topg - boot

        # interpolate surfaces to axes coords
        ds = ds[['icy', 'uplift', 'usurf', 'velsurf_mag']].interp(x=x, y=y)

    # interpolate srtm topography
    ds['topg'] = srtm.interp(x=x, y=y)

    # correct basal topo for uplift and pop nunataks
    ds['topg'] = ds.topg + ds.uplift.fillna(0.0)
    ds['icy'] = (ds.icy >= 0.5) * (ds.usurf > ds.topg)
    ds['usurf'] = ds.usurf.where(ds.icy)
    ds['velsurf_mag'] = ds.velsurf_mag.where(ds.icy)

    # return interpolated data
    return ds


# Styled plots from data arrays
# -----------------------------

def plot_ice_extent(darray, ax=None, ec='k', fc='none'):
    """Draw void or filled ice extent contour."""

    # plot a single contour
    if ec is not 'none':
        darray.plot.contour(ax=ax, colors=[ec], levels=[0.5], linewidths=0.25)
    if fc is not 'none':
        darray.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors=fc,
                             extend='neither', levels=[0.5, 1.5])


def plot_topo_contours(darray, ax=None, ec='0.25'):
    """Plot surface topography contours."""

    # contour levels
    levels = range(0, 5000, 200)
    majors = [l for l in levels if l % 1000 == 0]
    minors = [l for l in levels if l % 1000 != 0]

    # plot contours
    darray.plot.contour(ax=ax, colors=[ec], levels=majors, linewidths=0.25)
    darray.plot.contour(ax=ax, colors=[ec], levels=minors, linewidths=0.1)


def plot_shaded_relief(darray, ax=None, mode='co'):
    """Plot shaded relief map from elevation data array."""

    # plot basal topography
    if mode == 'gs':
        kwargs = dict(cmap='Greys', vmin=0, vmax=4500)
    else:
        kwargs = dict(cmap=ccv.ELEVATIONAL, vmin=-4500, vmax=4500)
    darray.plot.imshow(ax=ax, add_colorbar=False, zorder=-1, **kwargs)

    # add relief shading
    # FIXME: add xarray/numpy-centric functions in cartowik?
    shades = xr_multishading(darray)
    shades.plot.imshow(ax=ax, add_colorbar=False, cmap=ccv.SHINES,
                       vmin=-1.0, vmax=1.0, zorder=-1)

    # add coastline if data spans the zero
    if darray.min() * darray.max() < 0.0:
        colors = ('0.25' if mode == 'gs' else '#0978ab')
        darray.plot.contour(ax=ax, colors=colors, levels=[0.0],
                            linestyles=['dashed'], linewidths=0.25)


def plot_streamlines(dataset, ax=None, **kwargs):
    """Plot surface velocity streamlines."""

    # get current axes if none provided
    ax = ax or plt.gca()

    # extract velocities
    icy = dataset.thk.fillna(0.0) >= 1.0
    uvel = dataset.uvelsurf.where(icy).to_masked_array()
    vvel = dataset.vvelsurf.where(icy).to_masked_array()
    vmag = (uvel**2+vvel**2)**0.5

    # streamplot colormapping fails on empty arrays
    # FIXME report this as a bug in matplotlib
    if uvel.count() * vvel.count() == 0:
        return

    # add streamplot,
    ax.streamplot(dataset.x, dataset.y, uvel, vvel, color=vmag,
                  cmap='Blues', norm=mcolors.LogNorm(1e1, 1e3),
                  arrowsize=0.25, linewidth=0.5, **kwargs)


# Figure saving
# -------------

def save_animation_frame(func, outdir, t, *args, **kwargs):
    """Save figure produced by func as animation frame if missing."""

    # check if file exists
    fname = os.path.join(outdir, '{:06d}.png').format(t+120000)
    if not os.path.isfile(fname):

        # assemble figure and save
        print('plotting {:s} ...'.format(fname))
        fig = func(t, *args, **kwargs)
        fig.savefig(fname)
        plt.close(fig)


# Calculations on data arrays
# ---------------------------

def xr_gradient(darray):
    """Compute gradient along a all dimensions of a data array."""

    # extract coordinate data
    dims = darray.dims
    coords = [darray[d].data for d in dims]

    # apply numpy.gradient
    darray = xr.apply_ufunc(np.gradient, darray, *coords,
                            input_core_dims=(dims,)+dims,
                            output_core_dims=[('n',)+dims])

    # add vector component coordinate
    darray = darray.assign_coords(n=list(dims))

    # return as single dataarray
    return darray


def xr_shading(darray, azimuth=315.0, altitude=30.0, transparent=False):
    """Compute shaded relief map from a data array."""

    # convert to rad
    azimuth *= np.pi / 180.
    altitude *= np.pi / 180.

    # compute cartesian coords of the illumination direction
    # for transparent shades set horizontal surfaces to zero
    xlight = np.sin(azimuth) * np.cos(altitude)
    ylight = np.cos(azimuth) * np.cos(altitude)
    zlight = (0.0 if transparent else np.sin(altitude))

    # compute hillshade (minus dot product of normal and light direction)
    v, u = xr_gradient(darray)
    shade = - (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)
    return shade


def xr_multishading(darray):
    """Compute shaded relief using multiple light sources."""

    # compute relief shading
    s300 = xr_shading(darray, azimuth=300.0, altitude=30.0, transparent=True)
    s315 = xr_shading(darray, azimuth=315.0, altitude=30.0, transparent=True)
    s330 = xr_shading(darray, azimuth=330.0, altitude=30.0, transparent=True)
    return (s300+2.0*s315+s330)/4.0
