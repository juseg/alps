#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import iceplotlib.plot as iplt
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation

velonorm = LogNorm(1e1, 1e3)

def draw(t, ax):
    """What to draw at each animation step."""
    print 'plotting at %.1f ka...' % (-t/1e3)
    ax.cla()

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys')
    im = nc.imshow('thk', ax, t, vmin=0.0, vmax=3e3,
                   cmap='Blues_r', alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=range(0, 4000, 1000),
                    colors='k', linewidths=0.25)
    cs = nc.icemargin(ax, t, linewidths=0.5)
    ax.text(0.05, 0.90, '%.1f ka' % (-t/1e3), transform=ax.transAxes)

    # return mappable for colorbar
    return im

# load data
filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-2km/'
            'epica3222cool0950+acyc1+esia5/y???????-extra.nc')
nc = iplt.load(filepath)
time = nc.variables['time'][:]/(365.0*24*60*60)

# initialize figure
figw, figh = 135.01, 80.01
fig, ax = iplt.subplots_mm(figsize=(figw, figh),
                           left=2.5, right=20.0, bottom=2.5, top=2.5)
cax = fig.add_axes([1-17.5/figw, 2.5/figh, 5.0/figw, 1-5.0/figh])

# draw first frame and colorbar
im = draw(time[0], ax)
cb = fig.colorbar(im, cax)
cb.set_label(r'ice thickness (m)')

# make animation
anim = FuncAnimation(fig, draw, frames=time, fargs=(ax,))
anim.save('animation.mp4', fps=25, codec='h264')
#anim.save('animation.ogg', fps=25, codec='theora')

# close nc file
nc.close()
