#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import scipy as sp
import matplotlib.colors as mcolors
import cartopy.io.shapereader as shpreader

# profile parameters
regions = ['rhine', 'rhone', 'ivrea', 'isere', 'inn', 'taglia']
labels = ['Rhine', 'Rhone', 'Dora Baltea', u'Isère', 'Inn', 'Tagliamento']
colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
colors = [ut.pl.palette['dark'+hue] for hue in colors]
direcs = [1, -1, -1, 1, 1, -1]

# initialize figure
fig, ax, cax, scax, tsax = ut.pl.subplots_cax_sc_ts_nat()

# Map axes
# --------

# read postprocessed data
maxthksrf, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthksrf')
maxthkage, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxthkage')
maxicethk, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxicethk')
warmbased, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'warmbased')

# set contour levels, colors and hatches
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]

# plot
cs = ax.contourf(warmbased, levels=[0e3, 1e3], extent=extent, hatches=['////'])
cs = ax.contour(warmbased, [1e3], extent=extent, colors='0.25', linewidths=0.25)
im = ax.contourf(maxthkage/1e3, levs, extent=extent, colors=cols, extend='both', alpha=0.75)

# add colorbar
cb = fig.colorbar(im, cax, orientation='horizontal')
cb.set_label(r'age of maximum ice surface elevation (ka)')

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_envelope(ax)
ut.pl.draw_natural_earth(ax)
ut.pl.draw_glacier_names(ax)

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
t = nc.variables['time'][9::10]/(365.0*24*60*60)
h = nc.variables['thk'][9::10]
nc.close()


# Trimlines scatter plot
# ----------------------

# read trimlines data
trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                          dtype=None, delimiter=',', names=True)
xt = trimlines['x']
yt = trimlines['y']
zt = trimlines['z']/1e3

# convert to UTM 32
xt, yt, zt = ut.pl.utm.transform_points(ut.pl.swiss, xt, yt, zt).T

# draw trimlines on map
sc = ax.scatter(xt, yt, c='k', s=4**2, alpha=0.25)

# load boot topography
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
boot = nc.variables['topg'][:]
nc.close()

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
ht = sp.interpolate.interpn((y, x), maxicethk[::-1], (yt, xt), method='linear')/1e3
at = sp.interpolate.interpn((y, x), maxthkage[::-1], (yt, xt), method='linear')/1e3
bt = sp.interpolate.interpn((x, y), boot, (xt, yt), method='linear')/1e3

# set contour levels and colors
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]
cmap, norm = mcolors.from_levels_and_colors(levs, cols, extend='both')

# draw scatter plot
sc = scax.scatter(zt, (bt+ht), c=at, cmap=cmap, norm=norm, alpha=0.5)
scax.set_xlabel('observed trimline (km)')
scax.set_ylabel('compensated LGM surface (km)', y=2/5.)
scax.locator_params(axis='x', nbins=2)
scax.locator_params(axis='y', nbins=2)

# diff between compensated surface elevation and trimlines
dt = bt + ht - zt

# highlight mean thickness
zavg = zt.mean()
davg = dt.mean()
dstd = dt.std()
zz = [zt.min(), zt.max()]
scax.plot(zz, zz+davg, c='0.25')
scax.plot(zz, zz+davg-dstd, c='0.25', dashes=(2, 1), lw=0.5)
scax.plot(zz, zz+davg+dstd, c='0.25', dashes=(2, 1), lw=0.5)
scax.axvline(zavg, c='0.25', dashes=(2, 1), lw=0.5)
scax.axhline(zavg+davg, c='0.25', dashes=(2, 1), lw=0.5)
scax.text(zavg-0.025, (bt+ht).min(), '%.0f m' % (zavg*1e3), color='0.25',
          rotation=90, rotation_mode='anchor')
scax.text(zz[0], zavg+davg+0.025, '%.0f m' % ((zavg+davg)*1e3), color='0.25')


# Glacier profiles
# ----------------

# init new axes
twax = tsax.twinx()
twax.set_ylim((-300.0, 500.0))
twax.set_ylabel('glacier length (km)')

# loop on regions
for i, reg in enumerate(regions):
    c = colors[i]
    d = direcs[i]
    label = labels[i]

    # read profile from shapefile
    filename = '../data/native/profile_%s.shp' % reg
    shp = shpreader.Reader(filename)
    geom = shp.geometries().next()
    geom = geom[0]
    xp, yp = np.array(geom).T
    del shp, geom

    # add profile line
    ax.plot(xp, yp, c=c, dashes=(2, 1))
    ax.plot(xp[0], yp[0], c=c, marker='o')

    # extract space-time slice
    xi = t[:, None], yp[None, :], xp[None, :]  # coords to sample at
    hp = sp.interpolate.interpn((t, y, x), h, xi, method='linear')

    # compute distance along profile
    dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()
    dp = d * np.insert(dp, 0, 0.0)

    # plot envelope
    cs = twax.contourf(-t/1e3, dp/1e3, hp.T, levels=[1.0, 5e3], colors=[c], alpha=0.75)

# save figure
fig.savefig('alpcyc_hr_dynamics')
