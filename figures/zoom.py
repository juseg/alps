#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import iceplotlib.plot as iplt
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
import cartopy.feature as cfeature

velnorm = LogNorm(1e1, 1e3)

# cartopy features
rivers = cfeature.NaturalEarthFeature(
    category='physical', name='rivers_lake_centerlines', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.5)
lakes = cfeature.NaturalEarthFeature(
    category='physical', name='lakes', scale='10m',
    edgecolor='0.25', facecolor='0.85', lw=0.25)
coastline = cfeature.NaturalEarthFeature(
    category='physical', name='coastline', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.25)
graticules = cfeature.NaturalEarthFeature(
    category='physical', name='graticules_1', scale='10m',
    edgecolor='0.25', facecolor='none', lw=0.1)

# contour levels
levs = range(0, 4000, 100)
outer_levs = [l for l in levs if l % 1000 == 0]
inner_levs = [l for l in levs if l % 1000 != 0]

# drawing function
def draw(t, ax, cursor):
    """What to draw at each animation step."""
    age = -t/1e3
    #print 'plotting at %.1f ka...' % age
    ax.cla()

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.imshow('velsurf_mag', ax, t, norm=velnorm, cmap='Blues', alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=inner_levs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=outer_levs,
                    colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.5)
    ax.text(0.05, 0.90, '%.1f ka' % age, transform=ax.transAxes)

    # add cartopy vectors
    ax.add_feature(rivers, zorder=0)
    ax.add_feature(lakes, zorder=0)
    ax.add_feature(coastline, zorder=0)
    ax.add_feature(graticules)

    # update cursor
    cursor.set_data(age, (0, 1))

    # return mappable for colorbar
    return im

# initialize figure
figw, figh = 135.01, 120.01
fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=ccrs.UTM(32),
                           left=2.5, right=20.0, bottom=42.5, top=2.5)
tsax = fig.add_axes([12.5/figw, 10.0/figh, 1-25.0/figw, 30.0/figh])
cax = fig.add_axes([1-17.5/figw, 42.5/figh, 5.0/figw, 1-45.0/figh])
ax.set_rasterization_zorder(2.5)

# load temperature signal
filepath = ('/home/juliens/pism/input/dt/epica3222cool0950.nc')
nc = iplt.load(filepath)
age = -nc.variables['time'][:]/1e3
dt = nc.variables['delta_T'][:]
nc.close()

# plot time series
tsax.plot(age, dt, c='0.25')
tsax.set_xlabel('model age (ka)')
tsax.set_ylabel('temperature offset (K)', color='0.25')
tsax.set_ylim(-12.5, 7.5)

# load time series data
filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-1km/'
            'epica3222cool0950+acyc1+esia5/y???????-ts.nc')
nc = iplt.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# plot time series
tsax=tsax.twinx()
tsax.plot(age, vol, c='#1f78b4')
tsax.set_ylabel('ice volume (m s.l.e.)', color='#1f78b4')
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-0.05, 0.35)
tsax.locator_params(axis='y', nbins=6)
tsax.grid(axis='y')

# init moving vertical line
cursor = tsax.axvline(0.0, c='k', lw=0.25)

# load extra data
filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-1km/'
            'epica3222cool0950+acyc1+esia5/y???????-extra.nc')
nc = iplt.load(filepath)
time = nc.variables['time'][:]/(365.0*24*60*60)

# draw first frame and colorbar
im = draw(-25e3, ax, cursor)
cb = fig.colorbar(im, cax)
cb.set_label(r'surface velocity ($m\,a^{-1}$)')

# zoom on Zürich
extents = [150e3, 600e3, 5000e3, 5300e3]  # Switzerland and more
extents = [400e3, 550e3, 5175e3, 5275e3]  # Zürich
ax.set_extent(extents, crs=ax.projection)

# add city of Zürich
ll = ccrs.PlateCarree()
ax.plot(8.55, 47.366667, 'ko', transform=ll)
ax.text(465e3, 5250e3, 'Zurich', ha='center')

# close nc file
nc.close()

# save figure
fig.savefig('zoom')
