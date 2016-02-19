#!/usr/bin/env python2
# coding: utf-8

# FIXME: make iceplotlib a package
import sys
sys.path.append('iceplotlib')

import iceplotlib.plot as iplt

# parameters
t = -65e3
confargs = ['', '+esia5']
labels = ['$E_{SIA}$ = 2', '$E_{SIA}$ = 5']

# initialize figure
figw, figh = 90.0, 145.0
fig, grid = iplt.subplots_mm(nrows=3, ncols=1, sharex=True, sharey=True,
                             figsize=(figw, figh),
                             left=2.5, right=20.0, bottom=2.5, top=2.5,
                             hspace=2.5, wspace=2.5)
cax1 = fig.add_axes([1-17.5/figw, 50.0/figh, 5.0/figw, 92.5/figh])
cax2 = fig.add_axes([1-17.5/figw, 2.5/figh, 5.0/figw, 45.0/figh])

# loop on different simulations
z = [None]*2
for i, conf in enumerate(confargs):
    ax = grid[i]
    ax.set_rasterization_zorder(2.5)

    # open extra file
    filepath = ('/home/juliens/pism/output/0.7.3/alps-wcnn-5km/'
                'epica3222cool1000+acyc1%s/y???????-extra.nc' % conf)
    nc = iplt.load(filepath)
    x, y, z[i] = nc._extract_xyz('usurf', t)

    # plot
    im = nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys')
    im = nc.imshow('thk', ax, t, vmin=0.0, vmax=3e3,
                   cmap='Blues', alpha=0.75)
    cs = nc.contour('usurf', ax, t, levels=range(0, 4000, 500),
                    colors='k', linewidths=0.25)
    cs = nc.icemargin(ax, t, linewidths=0.5)

    # annotate
    ax.text(0.05, 0.90, labels[i], transform=ax.transAxes)

# plot reference topo and margin
ax = grid[2]
nc.imshow('topg', ax, t, vmin=0.0, vmax=3e3, cmap='Greys')
nc.icemargin(ax, t, linewidths=0.5)
nc.close()

# plot difference
zdiff = z[1] - z[0]
w = (3*x[0]-x[1])/2
e = (3*x[-1]-x[-2])/2
n = (3*y[0]-y[1])/2
s = (3*y[-1]-y[-2])/2
cs = ax.imshow(zdiff, extent=(w, e, n, s), vmin=-5e2, vmax=5e2, cmap='RdBu', alpha=0.75)
ax.text(0.05, 0.90, 'difference', transform=ax.transAxes)

# add colorbars and save
cb = fig.colorbar(im, cax1, extend='max')
cb.set_label(r'ice thickness (m)')
cb = fig.colorbar(cs, cax2, extend='both')
cb.set_label(r'surf. elev. diff. (m)')
fig.savefig('outmap_sensrheo')
