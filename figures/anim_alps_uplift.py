#!/usr/bin/env python2
# coding: utf-8

import util as ut
import iceplotlib.plot as iplt
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs

# elevation contour levels
levs = range(0, 4000, 200)
outer_levs = [l for l in levs if l % 1000 == 0]
inner_levs = [l for l in levs if l % 1000 != 0]

# uplift contour levels and colors
levs = [-0.01, -0.003, -0.001, 0.0, 0.001, 0.003, 0.01]
cmap = iplt.get_cmap('PRGn', len(levs)+1)
cols = cmap(range(len(levs)+1))

# drawing function
def draw(t, ax, cursor):
    """What to draw at each animation step."""
    age = -t/1e3
    print 'plotting at %.1f ka...' % age
    ax.cla()

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.contourf('dbdt', ax, t, levels=levs, extend='both',
                     colors=cols, thkth=-1, alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=inner_levs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=outer_levs,
                    colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)
    ax.text(0.05, 0.90, '%.1f ka' % age, transform=ax.transAxes)

    # add cartopy vectors
    ut.pl.draw_natural_earth(ax)

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

# add signature
fig.text(1-2.5/figw, 2.5/figh, 'J. Seguinot et al. (2016)',
         ha='right', va='bottom')

# load time series data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/ts.nc'
nc = ut.io.load(filepath)
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
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
time = nc.variables['time'][::]/(365.0*24*60*60)
dbdt = nc.variables['dbdt'][::]
dvdt = dbdt.sum(axis=(1, 2))*1e-3

# plot time series
tsax = tsax.twinx()
tsax.plot(-time/1e3, dvdt, c='#33a02c')
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-11.25, 6.25)
tsax.set_ylabel('volumic uplift rate ($km^{3}\,a^{-1}$)',
                labelpad=0, color='#33a02c')
tsax.locator_params(axis='y', nbins=6)
tsax.grid(axis='y')

# init moving vertical line
cursor = tsax.axvline(0.0, c='k', lw=0.25)

# draw first frame and colorbar
im = draw(time[0], ax, cursor)
cb = fig.colorbar(im, cax)
cb.set_label(r'uplift rate ($m\,a^{-1}$)', labelpad=0)

# make animation
anim = FuncAnimation(fig, draw, frames=time, fargs=(ax, cursor))
anim.save('anim_alps_uplift.mp4', fps=25, codec='h264')
anim.save('anim_alps_uplift.ogg', fps=25, codec='theora')

# close nc file
nc.close()
