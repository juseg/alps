#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp
import iceplotlib.plot as iplt
import cartopy.io.shapereader as shpreader
from scipy import interpolate

# parameters
reg = 'rhine'
tp = [-27e3, -25e3, -23e3, -21e3]

# initialize figure
mode = 'column'
figw, figh = (177.0, 85.0) if mode == 'page' else (85.0, 60.0)
fig, grid = iplt.subplots_mm(nrows=1, ncols=len(tp), sharex=True, sharey=True,
                             figsize=(figw, figh),
                             gridspec_kw=dict(left=12.0, right=1.5,
                                              bottom=9.0, top=1.5,
                                              hspace=1.5, wspace=1.5))

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
h = nc.variables['thk'][tidx]
T = nc.variables['temp_pa'][tidx]

# extract space-time slice
xi = tp[:, None], yp[None, :], xp[None, :]  # coords to sample at
hp = sp.interpolate.interpn((t, y, x), h, xi, method='linear')
Tp = sp.interpolate.interpn((t, y, x), T, xi, method='linear')

# compute distance along profile
dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
dp = np.insert(dp, 0, 0.0)

# mask above ice surface
# FIXME

# plot profiles
for i, ax in enumerate(grid):
    cs = ax.plot(hp[i].T/1e3, dp/1e3, 'k-')
    cs = ax.contourf(z/1e3, dp/1e3, Tp[i], cmap='Blues_r')
    ut.pl.add_subfig_label('%.0f ka' % (-t[i]/1e3), ax=ax)

# add colorbar
# FIXME

# close extra file
nc.close()

# set axes properties
grid[0].set_xlim(2.25, -0.25)
grid[0].set_ylabel('glacier length (km)')
grid[len(tp)/2].set_xlabel('ice thickness (km)')

# save
ut.pl.savefig()
