#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import cartopy.io.shapereader as cshp

# initialize figure
fig, ax, cax1, cax2, tsax = ut.pl.subplots_cax_ts_big()

# time for plot
a = 21.0
t = -a*1e3

# location of time series
xts, yts = 600e3, 5170e3


# Map axes
# --------

# load extra data
filepath = 'output/0.7.3-craypetsc/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
its = np.argmin(abs(x-xts))
jts = np.argmin(abs(y-yts))
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
dbdt = nc.variables['dbdt'][:, its, jts]*1e3

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
cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs,
                colors='0.25', linewidths=0.1)
cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs,
                colors='0.25', linewidths=0.25)
cs.clabel(color='0.25', fmt='%d', linewidths=0.5)

# surface velocity
qv = nc.quiver('velsurf', ax, t, scale=250.0, width=0.25*25.4/72/800.0,
               norm=ut.pl.velnorm, cmap='Blues', zorder=2)

# central point for uplift
ax.plot(xts, yts, 'o', c=ut.pl.palette['darkgreen'])

# add colorbars
cb = fig.colorbar(qv, cax1, orientation='horizontal', extend='both')
cb.set_label(r'ice surface velocity ($m\,a^{-1}$)')
cb = fig.colorbar(im, cax2, orientation='horizontal', extend='both',
                  ticks=range(0, 3001, 1000))
cb.set_label(r'bedrock topography (m)')

# add vectors
ut.pl.draw_natural_earth(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_footprint(ax)
ut.pl.add_corner_tag('%.1f ka' % a, ax)

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
        ax.plot(xc, yc, 'ko')
        ax.annotate(name, xy=(xc, yc), xytext=(dx, dy),
                    textcoords='offset points', ha=ha, va=va, clip_on=True)



# Time series
# -----------

# prepare parasite axes
ax0 = tsax
ax1 = ax0.twinx()
ax2 = ax0.twinx()
ax0.spines['left'].set_edgecolor('0.25')
ax1.spines['right'].set_edgecolor(ut.pl.palette['darkblue'])
ax2.spines['right'].set_edgecolor(ut.pl.palette['darkgreen'])
ax2.spines['right'].set_position(('axes', 1+15.0/205.0))
ax0.tick_params(axis='y', colors='0.25')
ax1.tick_params(axis='y', colors=ut.pl.palette['darkblue'])
ax2.tick_params(axis='y', colors=ut.pl.palette['darkgreen'])

# set bounds
ax0.set_xlim(120.0, 0.0)
ax0.set_ylim(-12.5, 7.5)
ax1.set_ylim(-0.05, 0.35)
ax2.set_ylim(-15.0, 25.0)

# limit ticks
ax0.locator_params(axis='y', nbins=6)
ax1.locator_params(axis='y', nbins=6)
ax2.locator_params(axis='y', nbins=6)

# add labels
ax1.set_ylabel('ice volume (m s.l.e.)', color=ut.pl.palette['darkblue'])
ax2.set_ylabel('uplift rate ($mm\,a^{-1}$)', color=ut.pl.palette['darkgreen'])

# plot central uplift rate
ax2.plot(age, dbdt, c=ut.pl.palette['darkgreen'])
ax2.plot(0.0, dbdt[-1], 'o',
         ms=6, c='w', mec=ut.pl.palette['darkgreen'], mew=1.0, clip_on=False)
nc.close()

# load ts output
filepath = 'output/0.7.3-craypetsc/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# plot ice volume
ax1.plot(age, vol, c=ut.pl.palette['darkblue'])
ax1.plot(a, vol[((age-a)**2).argmin()], 'o',
         ms=6, c='w', mec=ut.pl.palette['darkblue'], mew=1.0)

# add grid and vertical line
ax1.axvline(a, c='k', lw=0.25)
ax1.grid(axis='y')

# save figure
fig.savefig('alpcyc_hr_lgmbig')
