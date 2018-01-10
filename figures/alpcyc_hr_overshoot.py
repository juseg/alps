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
regions = ['rhine', 'rhone']
labels = ['Rhine', 'Rhone']
cmaps = ['Blues_r', 'Greens_r']
cmaps = ['RdBu_r']*2
tp = range(-28000, -22000+1, 1000)

# initialize figure
mode = 'page'
figw, figh = (177.0, 85.0) if mode == 'page' else (85.0, 60.0)
fig, grid = iplt.subplots_mm(nrows=len(regions), ncols=len(tp),
                             figsize=(figw, figh), sharex=True, sharey='row',
                             gridspec_kw=dict(left=12.0, right=15.0,
                                              bottom=9.0, top=1.5,
                                              hspace=1.5, wspace=0.0))
caxes = fig.subplots_mm(nrows=len(regions), ncols=1,
                        gridspec_kw=dict(left=figw-13.5, right=10.5,
                                         bottom=9.0, top=1.5,
                                         hspace=1.5, wspace=0.0))
#cax = fig.add_axes([1-13.5/figw, 9.0/figh, 3.0/figw, 1-10.5/figh])

# load final data
filepath = ut.alpcyc_bestrun + 'y???????.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
z = nc.variables['z'][:]
t = nc.variables['time'][:]/(365.0*24*60*60)

# find nearest time indices
tp = np.array(tp)
tidx = ((t[:, None]-tp[None, :])**2).argmin(axis=0)
t = t[tidx]
b = nc.variables['topg'][tidx]
s = nc.variables['usurf'][tidx]
T = nc.variables['temp_pa'][tidx]

# loop on regions
for i, reg in enumerate(regions):
    cax = caxes[i]
    axes = grid[i]
    cmap = cmaps[i]
    label = labels[i]


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
    levs = range(-18, 1, 2)
    cols = plt.get_cmap(cmap, len(levs))(range(len(levs)))

    # for each axes
    for j, ax in enumerate(axes):

        ## change spine visibility
        #ax.spines['left'].set_color('none')
        #ax.spines['right'].set_position('zero')

        # plot topographic profiles
        ax.plot(bp[j].T/1e3, dp/1e3, 'k-', lw=0.5)
        ax.plot(sp[j].T/1e3, dp/1e3, 'k-', lw=0.5)

        # prepare triangulation
        trix = zz[j].flatten()/1e3
        triy = dd[j].flatten()/1e3
        triang = tri.Triangulation(trix, triy)

        # set mask above ice surface
        mask = (zz[j] > sp[j, :, None] - 1.0).flatten()
        mask = np.all(mask[triang.triangles], axis=1)
        triang.set_mask(mask)

        # masking badly shaped triangles at the border of the triangular mesh.
        mask = tri.TriAnalyzer(triang).get_flat_tri_mask(0.01)
        triang.set_mask(mask)

        # plot temperature profile
        cs = ax.tricontourf(triang, Tp[j].flatten(),
                            levels=levs, colors=cols, extend='min')

        # add age tag
        agetag = '%.0f ka' % (-t[j]/1e3) + ('\n'+label if j == 0 else '')
        ut.pl.add_subfig_label(agetag, ax=ax)

    # add y label
    grid[i, 0].set_ylabel(label + ' glacier length (km)')

    # add colorbar
    cb = fig.colorbar(cs, cax)
    cb.set_label(u'ice temperature (°C)')

# set axes properties
grid[0, 0].set_xlim(3.75, -0.25)
grid[-1, len(tp)/2].set_xlabel('elevation (km)')

# close extra file
nc.close()

# save
ut.pl.savefig()
