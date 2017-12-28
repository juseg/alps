#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import cartopy.io.shapereader as shpreader
import scipy.interpolate as sinterpolate
import iceplotlib.plot as iplt

# parameters
reg = 'rhine'
tp = [-27e3, -25e3, -23e3, -21e3]

# initialize figure
mode = 'column'
figw, figh = (177.0, 85.0) if mode == 'page' else (85.0, 60.0)
fig, grid = iplt.subplots_mm(nrows=1, ncols=len(tp), sharex=True, sharey=True,
                             figsize=(figw, figh),
                             gridspec_kw=dict(left=12.0, right=15.0,
                                              bottom=9.0, top=1.5,
                                              hspace=1.5, wspace=1.5))
cax = fig.add_axes([1-13.5/figw, 9.0/figh, 3.0/figw, 1-10.5/figh])

# load final data
filepath = ut.alpcyc_bestrun + 'y???????.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
z = nc.variables['z'][:]
t = nc.variables['time'][:]/(365.0*24*60*60)


# Map axes
# --------

# read profile from shapefile
filename = '../data/native/profile_%s.shp' % reg
shp = shpreader.Reader(filename)
geom = shp.geometries().next()
geom = geom[0]
xp, yp = np.array(geom).T
del shp, geom

## add profile line
#ax.plot(xp, yp, c=c, dashes=(2, 1))
#ax.plot(xp[0], yp[0], c=c, marker='o')


# Time series
# -----------

# find nearest time indices
tp = np.array(tp)
tidx = ((t[:, None]-tp[None, :])**2).argmin(axis=0)
t = t[tidx]
b = nc.variables['topg'][tidx]
s = nc.variables['usurf'][tidx]
T = nc.variables['temp_pa'][tidx]

# extract space-time slice
xi = tp[:, None], yp[None, :], xp[None, :]  # coords to sample at
bp = sinterpolate.interpn((t, y, x), b, xi, method='linear')
sp = sinterpolate.interpn((t, y, x), s, xi, method='linear')
Tp = sinterpolate.interpn((t, y, x), T, xi, method='linear')

# compute distance along profile
dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
dp = np.insert(dp, 0, 0.0)

# create mesh grid and add basal topo
dd, tt, zz = np.meshgrid(dp, tp, z)
zz += bp[:, :, None]

# set contour levels, colors and hatches
levs = range(-18, 1, 3)
cmap = plt.get_cmap('Blues_r', len(levs))
cols = cmap(range(len(levs)))

# for each axes
for i, ax in enumerate(grid):

    # plot topographic profiles
    ax.plot(bp[i].T/1e3, dp/1e3, 'k-', lw=0.5)
    ax.plot(sp[i].T/1e3, dp/1e3, 'k-', lw=0.5)

    # prepare triangulation
    trix = zz[i].flatten()/1e3
    triy = dd[i].flatten()/1e3
    triang = tri.Triangulation(trix, triy)

    # set mask above ice surface
    mask = (zz[i] > sp[i, :, None]).flatten()
    mask = np.all(mask[triang.triangles], axis=1)
    triang.set_mask(mask)

    # plot temperature profile
    cs = ax.tricontourf(triang, Tp[i].flatten(),
                        levels=levs, colors=cols, extend='min')
    ut.pl.add_subfig_label('%.0f ka' % (-t[i]/1e3), ax=ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(u'ice temperature (°C)')

# close extra file
nc.close()

# set axes properties
grid[0].set_xlim(3.5, -0.5)
grid[0].set_ylabel('glacier length (km)')
grid[len(tp)/2].set_xlabel('elevation (km)')

# save
ut.pl.savefig()
