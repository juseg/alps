#!/usr/bin/env python2
# coding: utf-8

import util as ut
import iceplotlib.plot as iplt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# initialize figure
figw, figh = 282.5, 65.0
fig, grid = iplt.subplots_mm(figsize=(figw, figh), projection=ccrs.UTM(32),
                             nrows=1, ncols=4, sharex=True, sharey=True,
                             left=2.5, right=2.5, bottom=17.5, top=2.5,
                             hspace=2.5, wspace=2.5)
cgrid = [fig.add_axes([(2.5+i*70.000)/figw, 10.0/figh, 67.5/figw, 5.0/figh])
         for i in range(4)]
for ax in grid.flat:
    ax.set_rasterization_zorder(2.5)

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

# plot boot topo and geographic features
nc = ut.io.load('input/boot/alps-srtm+gou11simi-1km.nc')
for ax in grid.flat:
    im = nc.imshow('topg', ax, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    ax.add_feature(rivers, zorder=0)
    ax.add_feature(lakes, zorder=0)
    ax.add_feature(coastline, zorder=0)
    ax.add_feature(graticules)

# plot boot geoflux on last panel
ax = grid.flat[3]
cax = cgrid[3]
levs = range(55, 96, 5)
cmap = iplt.get_cmap('PuOr_r', len(levs)-1)
cols = cmap(range(len(levs)-1))
cs = nc.contourf('bheatflx', ax, levels=levs, colors=cols, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='horizontal', ticks=levs[1::2])
cb.set_label(r'Geothermal flux ($mW\,m^{-2}$)')
nc.close()

# load atm file
# FIXME: add unit conversion to iceplotlib
nc = ut.io.load('input/atm/alps-wcnn-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
temp = nc.variables['air_temp'][6].T-273.15
prec = nc.variables['precipitation'][0].T*910.0/123
nc.close()

# load standard deviation file
# FIXME: add unit conversion to iceplotlib
nc = ut.io.load('input/sd/alps-erai-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
sd = nc.variables['air_temp_sd'][6].T
nc.close()

# plot July temperature
#print 'July temp min %.1f, max %.1f' % (temp.min(), temp[3:-3, 3:-3].max())
ax = grid.flat[0]
cax = cgrid[0]
levs = range(-5, 26, 5)
cmap = iplt.get_cmap('RdBu_r', len(levs)-1)
cols = cmap(range(len(levs)))
cs = ax.contourf(x, y, temp, levs, colors=cols, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='horizontal', ticks=levs[1::2])
cb.set_label(u'July temperature (°C)')

# plot January precipitation
#print 'Jan. prec min %.1f, max %.1f' % (prec.min(), prec.max())
ax = grid.flat[1]
cax = cgrid[1]
levs = range(0, 31, 5)
cmap = iplt.get_cmap('Greens', len(levs)-1)
cols = cmap(range(len(levs)))
cs = ax.contourf(x, y, prec, levs, colors=cols, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='horizontal', ticks=levs[::2])
cb.set_label(r'January precipitation (mm)')

# plot July standard deviation
#print 'July s.d. min %.1f, max %.1f' % (sd.min(), sd.max())
ax = grid.flat[2]
cax = cgrid[2]
levs = [1.7, 2.0, 2.3, 2.6, 2.9, 3.2, 3.5]
cmap = iplt.get_cmap('Reds', len(levs)-1)
cols = cmap(range(len(levs)-1))
cs = ax.contourf(x, y, sd, levs, colors=cols, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='horizontal', ticks=levs[1::2])
cb.set_label(u'July PDD SD (°C)')

# save
fig.savefig('inputs')
