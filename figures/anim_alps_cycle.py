#!/usr/bin/env python2
# coding: utf-8

import util as ut
from matplotlib.animation import FuncAnimation

# drawing function
def draw(t, ax, cursor):
    """What to draw at each animation step."""
    age = -t/1e3
    print 'plotting at %.1f ka...' % age
    ax.cla()
    ax.outline_patch.set_ec('none')

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.imshow('velsurf_mag', ax, t, norm=ut.pl.velnorm, cmap='Blues', alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs,
                    colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

    # add vectors
    ut.pl.draw_natural_earth(ax)
    ut.pl.draw_lgm_outline(ax)
    ut.pl.draw_footprint(ax)
    ut.pl.add_corner_tag('%.1f ka' % age, ax)

    # update cursor
    cursor.set_data(age, (0, 1))

    # return mappable for colorbar
    return im

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_anim()
ax.set_extent([150e3, 1050e3, 4820e3, 5420e3], crs=ax.projection)

# add signature
figw, figh = [dim*25.4 for dim in fig.get_size_inches()]
fig.text(1-2.5/figw, 2.5/figh, 'J. Seguinot et al. (in prep.)',
         ha='right', va='bottom')

# load time series data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/ts.nc'
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
cb = fig.colorbar(im, cax, extend='both')
cb.set_label(r'surface velocity ($m\,a^{-1}$)')

# make animation
anim = FuncAnimation(fig, draw, frames=time, fargs=(ax, cursor))
anim.save('anim_alps_cycle.mp4', fps=25, codec='h264')
anim.save('anim_alps_cycle.ogg', fps=25, codec='theora')

# close nc file
nc.close()
