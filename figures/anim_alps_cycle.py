#!/usr/bin/env python2
# coding: utf-8

import util as ut
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation

velonorm = LogNorm(1e1, 1e3)

# contour levels
levs = range(0, 4000, 200)
outer_levs = [l for l in levs if l % 1000 == 0]
inner_levs = [l for l in levs if l % 1000 != 0]

# drawing function
def draw(t, ax, cursor):
    """What to draw at each animation step."""
    age = -t/1e3
    print 'plotting at %.1f ka...' % age
    ax.cla()

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.imshow('velsurf_mag', ax, t, norm=velonorm, cmap='Blues', alpha=0.75)
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
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(labels=False)

# add signature
fig.text(1-2.5/figw, 2.5/figh, 'J. Seguinot et al. (2016)',
         ha='right', va='bottom')

# load temperature signal
nc = ut.io.load('input/dt/epica3222cool0950.nc')
age = -nc.variables['time'][:]/1e3
dt = nc.variables['delta_T'][:]
nc.close()

# plot time series
tsax.plot(age, dt, c='0.25')
tsax.set_xlabel('model age (ka)')
tsax.set_ylabel('temperature offset (K)', color='0.25')
tsax.set_ylim(-12.5, 7.5)

# load time series data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# plot time series
tsax=tsax.twinx()
tsax.plot(age, vol, c=ut.pl.palette['darkblue'])
tsax.set_ylabel('ice volume (m s.l.e.)', color=ut.pl.palette['darkblue'])
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-0.05, 0.35)
tsax.locator_params(axis='y', nbins=6)
tsax.grid(axis='y')

# init moving vertical line
cursor = tsax.axvline(0.0, c='k', lw=0.25)

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
time = nc.variables['time'][:]/(365.0*24*60*60)

# draw first frame and colorbar
im = draw(time[0], ax, cursor)
cb = fig.colorbar(im, cax)
cb.set_label(r'ice thickness (m)')

# make animation
anim = FuncAnimation(fig, draw, frames=time, fargs=(ax, cursor))
anim.save('anim_alps_cycle.mp4', fps=25, codec='h264')
anim.save('anim_alps_cycle.ogg', fps=25, codec='theora')

# close nc file
nc.close()
