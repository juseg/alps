#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import iceplotlib.plot as iplt
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation
from matplotlib.transforms import ScaledTranslation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as cshp

# time for plot
t = -21e3

# Initialize figure
# -----------------

# geographic projection and extent
ll = ccrs.PlateCarree()
utm = ccrs.UTM(32)
extent = 150e3, 1050e3, 4820e3, 5420e3 # model domain
extent = 155e3, 1045e3, 4825e3, 5415e3 # 5 km crop

# initialize figure
figw, figh = 405.0, 270.0
fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=utm,
                           left=2.5, right=2.5, bottom=2.5, top=2.5)
ax.set_rasterization_zorder(2.5)
ax.set_extent(extent, utm)
tsax = fig.add_axes([1-247.5/figw, 27.5/figh, 220.0/figw, 40.0/figh])
cax = fig.add_axes([22.5/figw, 1-87.5/figh, 5.0/figw, 55.0/figh])

# add white rectangles
kwa = dict(ec='k', fc='w', transform=fig.transFigure, zorder=3)
tsrect = iplt.Rectangle((1-262.5/figw, 12.5/figh), 250/figw, 75/figh, **kwa)
crect = iplt.Rectangle((12.5/figw, 1-97.5/figh), 30/figw, 75/figh, **kwa)
ax.add_patch(tsrect)
ax.add_patch(crect)

# Main panel
# ----------

# load extra data
nc = iplt.load('/home/juliens/pism/output/0.7.3/alps-wcnn-1km/'
               'epica3222cool0950+acyc1+esia5/y???????-extra.nc')

# contour levels and velocity norm
levs = range(0, 4000, 100)
outer_levs = [l for l in levs if l % 1000 == 0]
inner_levs = [l for l in levs if l % 1000 != 0]
velnorm = LogNorm(1e1, 1e3)

# bed topography
im = nc.imshow('topg', ax, t, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
#im = nc.shading('topg', ax, t, zorder=-1)

# frozen bed areas
cs = nc.contourf('temppabase', ax, t, levels=[-50.0, -1e-6],
                 cmap=None, colors='none', hatches=['//'], zorder=0)
cs = nc.contour('temppabase', ax, t, levels=[-50.0, -1e-6],
                colors='k', linewidths=0.25, linestyles=['-'], zorder=0)

# ice margin
cs = nc.icemarginf(ax, t, colors='w', alpha=0.75)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

# surface topography
cs = nc.contour('usurf', ax, t, levels=inner_levs,
                colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=outer_levs,
                colors='0.25', linewidths=0.25)
cs.clabel(color='0.25', fmt='%d', linewidths=0.5)

# surface velocity
qv = nc.quiver('velsurf', ax, t, scale=250.0, width=0.25*25.4/72/800.0,
               norm=velnorm, cmap='Blues', zorder=2)

# add cartopy vectors
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
ax.add_feature(rivers, zorder=0)
ax.add_feature(lakes, zorder=0)
ax.add_feature(coastline, zorder=0)
ax.add_feature(graticules)

# add lgm outline
shp = cshp.Reader('../data/native/lgm_alpen_holefilled.shp')
ax.add_geometries(shp.geometries(), ll, lw=0.5, alpha=0.75,
                  edgecolor='#e31a1c', facecolor='none', zorder=0)

# add colorbar
cb = fig.colorbar(qv, cax)
cb.set_label(r'surface velocity ($m\,a^{-1}$)')

# close extra file
nc.close()

# load temperature signal
nc = iplt.load('/home/juliens/pism/input/dt/epica3222cool0950.nc')
age = -nc.variables['time'][:]/1e3
dt = nc.variables['delta_T'][:]
nc.close()

# plot time series
tsax.plot(age, dt, c='0.25')
tsax.set_xlabel('model age (ka)')
tsax.set_ylabel('temperature offset (K)', color='0.25')
tsax.set_ylim(-12.5, 7.5)

# load time series data
nc = iplt.load('/home/juliens/pism/output/0.7.3/alps-wcnn-1km/'
               'epica3222cool0950+acyc1+esia5/y???????-ts.nc')
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

# add vertical line
tsax.axvline(21.0, c='k', lw=0.25)

# TODO:
# * SRTM topo
# * volumic uplift rate
# * model max extent
# * MIS stages

# save figure
fig.savefig('lgmbig')
