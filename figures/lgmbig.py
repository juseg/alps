#!/usr/bin/env python2
# coding: utf-8

import util as ut
import cartopy.io.shapereader as cshp

# initialize figure
fig, ax, cax1, cax2, tsax = ut.pl.subplots_cax_ts_big()

# time for plot
a = 21.0
t = -a*1e3


# Map axes
# --------

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)

# bed topography
im = nc.imshow('topg', ax, t, vmin=0e3, vmax=3e3, cmap='Greys', zorder=-1)
#im = nc.shading('topg', ax, t, zorder=-1)

# frozen bed areas
cs = nc.contourf('temppabase', ax, t, levels=[-50.0, -1e-6],
                 cmap=None, colors='none', hatches=['//'], zorder=0)
cs = nc.contour('temppabase', ax, t, levels=[-50.0, -1e-6],
                colors='k', linewidths=0.25, linestyles=['-'], zorder=0)

# footprint
x = nc.variables['x'][:]
y = nc.variables['y'][:]
thk = nc.variables['thk'][:]
duration = (thk >= 1.0).sum(axis=0)*0.1
footprint = (duration > 0)  # = 1 - (thk < 1.0).prod(axis=0)
cs = ax.contour(x, y, footprint.T, levels=[0.5],
                colors=[ut.pl.palette['darkorange']],
                linestyles=[(0, [3, 1])], linewidths=0.5, alpha=0.75)

# ice margin
cs = nc.icemarginf(ax, t, colors='w', alpha=0.75)
cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

# surface topography
cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs,
                colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs,
                colors='0.25', linewidths=0.25)
cs.clabel(color='0.25', fmt='%d', linewidths=0.5)

# surface velocity
qv = nc.quiver('velsurf', ax, t, scale=250.0, width=0.25*25.4/72/800.0,
               norm=ut.pl.velnorm, cmap='Blues', zorder=2)

# central point for uplift
ax.plot(nc['x'][450], nc['y'][350], 'o', c=ut.pl.palette['darkgreen'])

# close extra file
nc.close()

# add colorbars
cb = fig.colorbar(qv, cax1, orientation='horizontal', extend='both')
cb.set_label(r'ice surface velocity ($m\,a^{-1}$)')
cb = fig.colorbar(im, cax2, orientation='horizontal', extend='both',
                  ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')


# Geographic features
# -------------------

# add vectors
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)

# add cities
extent = ut.pl.regions['crop']
center = (extent[1]+extent[0])/2, (extent[3]+extent[2])/2
offset = 5
shp = cshp.Reader(cshp.natural_earth(resolution='10m',
                                     category='cultural',
                                     name='populated_places_simple'))
for rec in shp.records():
    name = rec.attributes['name'].decode('latin-1')
    rank = rec.attributes['scalerank']
    pop = rec.attributes['pop_max']
    lon = rec.geometry.x
    lat = rec.geometry.y
    if rank <= 7:
        xc, yc = ax.projection.transform_point(lon, lat, src_crs=ut.pl.ll)
        xloc = ('l' if xc < center[0] else 'r')
        yloc = ('l' if yc < center[1] else 'u')
        dx = {'c': 0, 'l': -1, 'r': 1}[xloc]*offset
        dy = {'c': 0, 'l': -1, 'u': 1}[yloc]*offset
        ha = {'c': 'center', 'l': 'right', 'r': 'left'}[xloc]
        va = {'c': 'center', 'l': 'top', 'u': 'bottom'}[yloc]
        i = abs(x-xc).argmin()
        j = abs(y-yc).argmin()
        d = duration[i, j]
        text = name + ('\n%.1f ka' % d if d > 0 else '')
        ax.plot(xc, yc, 'ko')
        ax.annotate(text, xy=(xc, yc), xytext=(dx, dy),
                    textcoords='offset points', ha=ha, va=va, clip_on=True)

# save figure
fig.savefig('lgmbig')
