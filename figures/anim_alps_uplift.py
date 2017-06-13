#!/usr/bin/env python2
# coding: utf-8

import util as ut
from matplotlib.animation import FuncAnimation

# uplift contour levels and colors
levs = [-0.01, -0.003, -0.001, 0.0, 0.001, 0.003, 0.01]
cmap = ut.pl.get_cmap('PRGn', len(levs)+1)
cols = cmap(range(len(levs)+1))

# drawing function
def draw(t, ax, cursor):
    """What to draw at each animation step."""
    age = -t/1e3
    print 'plotting at %.2f ka...' % age
    ax.cla()

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
    im = nc.contourf('dbdt', ax, t, levels=levs, extend='both',
                     colors=cols, thkth=-1, alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.inlevs,
                    colors='0.25', linewidths=0.1)
    cs = nc.contour('usurf', ax, t, levels=ut.pl.utlevs,
                    colors='0.25', linewidths=0.25)
    cs = nc.icemargin(ax, t, colors='k', linewidths=0.25)

    # add cartopy vectors
    ut.pl.draw_natural_earth(ax)
    ut.pl.add_corner_tag('%.1f ka' % a, ax)

    # update cursor
    cursor.set_data(age, (0, 1))

    # return mappable for colorbar
    return im

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts(labels=False)

# add signature
fig.text(1-2.5/figw, 2.5/figh, 'J. Seguinot et al. (2016)',
         ha='right', va='bottom')

# load time series data
filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
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
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
time = nc.variables['time'][::]/(365.0*24*60*60)
dbdt = nc.variables['dbdt'][::]
dvdt = dbdt.sum(axis=(1, 2))*1e-3

# plot time series
tsax = tsax.twinx()
tsax.plot(-time/1e3, dvdt, c=ut.pl.palette['darkgreen'])
tsax.set_xlim(120.0, 0.0)
tsax.set_ylim(-11.25, 6.25)
tsax.set_ylabel('volumic uplift rate ($km^{3}\,a^{-1}$)',
                labelpad=0, color=ut.pl.palette['darkgreen'])
tsax.locator_params(axis='y', nbins=6)
tsax.grid(axis='y')

# init moving vertical line
cursor = tsax.axvline(0.0, c='k', lw=0.25)

# draw first frame and colorbar
im = draw(time[0], ax, cursor)
cb = fig.colorbar(im, cax)
cb.set_label(r'uplift rate ($m\,a^{-1}$)', labelpad=0)

# make animation
anim = FuncAnimation(fig, draw, frames=time[9::10], fargs=(ax, cursor))
anim.save('anim_alps_uplift.mp4', fps=25, codec='h264')
anim.save('anim_alps_uplift.ogg', fps=25, codec='theora')

# close nc file
nc.close()
