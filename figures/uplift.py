#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import iceplotlib.plot as iplt
from matplotlib.transforms import ScaledTranslation
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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

# initialize figure
figw, figh = 135.01, 120.01
fig, ax = iplt.subplots_mm(figsize=(figw, figh), projection=ccrs.UTM(32),
                           left=2.5, right=20.0, bottom=42.5, top=2.5)
tsax = fig.add_axes([12.5/figw, 10.0/figh, 1-25.0/figw, 30.0/figh])
cax = fig.add_axes([1-17.5/figw, 42.5/figh, 5.0/figw, 1-45.0/figh])
ax.set_rasterization_zorder(2.5)

# load time series data
filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-2km/'
            'epica3222cool0950+acyc1+esia5/y???????-ts.nc')
nc = iplt.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# plot time series
tsax.plot(age, vol, c='0.25')
tsax.set_ylabel('ice volume (m s.l.e.)', color='0.25')
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-0.05, 0.65)
tsax.locator_params(axis='y', nbins=6)
tsax.grid(axis='y')

# load extra data
# FIXME: implement unit conversion (m to mm) in iceplotlib
filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-1km/'
            'epica3222cool0950+acyc1+esia5/y???????-extra.nc')
nc = iplt.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
dbdt = nc.variables['dbdt'][:]

# compute volumic uplift rate time series
dvdt = dbdt.sum(axis=(1, 2))*1e-3
dbdt = dbdt[-1].T*1e3

# plot time series
tsax = tsax.twinx()
tsax.plot(age, dvdt, c='#33a02c')
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-11.25, 6.25)
tsax.set_ylabel('volumic uplift rate ($km^{3}\,a^{-1}$)',
                labelpad=0, color='#33a02c')
tsax.locator_params(axis='y', nbins=6)
tsax.grid(axis='y')

# plot modern uplift
im = nc.imshow('topg', ax, -1, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, dbdt, cmap='Greens', thkth=-1, alpha=0.75)

# add cartopy vectors
ax.add_feature(rivers, zorder=0)
ax.add_feature(lakes, zorder=0)
ax.add_feature(coastline, zorder=0)
ax.add_feature(graticules)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'modern uplift rate ($mm\,a^{-1}$)', labelpad=0)

# close nc file
nc.close()

# add subfigure labels
offset = ScaledTranslation(2.5/25.4, -2.5/25.4, fig.dpi_scale_trans)
ax.text(0, 1, '(a)', ha='left', va='top', fontweight='bold',
        transform=ax.transAxes + offset)
tsax.text(0, 1, '(b)', ha='left', va='top', fontweight='bold',
          transform=tsax.transAxes + offset)

# save figure
fig.savefig('uplift')
