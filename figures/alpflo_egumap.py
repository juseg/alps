#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import cartopy.io.shapereader as shpreader
import scipy.interpolate as sinterp
import matplotlib.colors as mcolors

# initialize figure
fig, ax, cax1, cax2, tsax = ut.fi.subplots_cax_ts_egu()

# personal colormaps
# FIXME move to ut.cm
cols = [(0.0, (1,1,1,1)), (0.5, (1,1,1,0)),
        (0.5, (0,0,0,0)), (1.0, (0,0,0,1))]  # white transparent black
shinemap = mcolors.LinearSegmentedColormap.from_list('shines', cols)

# time for plot
t = -24533.6

# estimate sea level drop
nc = ut.io.load('input/dsl/specmap.nc')
dsl = np.interp(t, nc.variables['time'][:], nc.variables['delta_SL'][:])
nc.close()

# load SRTM bedrock topography
srb, sre = ut.io.open_gtif('../data/external/srtm.tif')
srx, sry = ut.pl.coords_from_extent(sre, *srb.shape[::-1])

# load boot topo
filepath = 'input/boot/alps-srtm+thk+gou11simi-500m.nc'
nc = ut.io.load(filepath)
bx, by, bref = nc._extract_xyz('topg', 0)
nc.close()

# load extra data
filepath = ut.alpflo_bestrun + 'y0095480-extra.nc'
nc = ut.io.load(filepath)
ncx, ncy, ncb = nc._extract_xyz('topg', t)
ncx, ncy, ncs = nc._extract_xyz('usurf', t)

# interpolate boot topo to extra data
# FIXME needed because of mistake in Mx and My
bi = srb
bref = sinterp.interp2d(bx, by, bref, kind='quintic')(ncx, ncy)

# compute bedrock uplift
ncu = ncb - bref

# interpolate surfaces to SRTM coords (interp2d seem faster than interp)
print "interpolating surfaces..."
bi = srb
si = sinterp.interp2d(ncx, ncy, ncs, kind='quintic')(srx, sry)[::-1]
mi = sinterp.interp2d(ncx, ncy, ncs.mask, kind='quintic')(srx, sry)[::-1]
ui = sinterp.interp2d(ncx, ncy, ncu, kind='quintic')(srx, sry)[::-1]
mi = (mi > 0.5) + (si < bi)
si = np.ma.masked_array(si, mi)

# correct basal topo for uplift and sea-level drop
bi = bi + ui - dsl

# compute relief shading
sh = sum(ut.pl.shading(bi, azimuth=a, extent=sre, altitude=30.0,
                       transparent=True) for a in [300.0, 315.0, 330.0])/3.0

# plot interpolated results
print "plotting surfaces..."
im = ax.imshow(bi, extent=sre, vmin=-3e3, vmax=3e3, cmap=ut.cm.topo, zorder=-1)
sm = ax.imshow(sh, extent=sre, vmin=-1.0, vmax=1.0, cmap=shinemap, zorder=-1)
cs = ax.contour(bi, extent=sre, levels=[0.0], colors='#0978ab')
cs = ax.contourf(srx, sry, mi, levels=[0.0, 0.5], colors='w', alpha=0.75)
cs = ax.contour(srx, sry, mi, levels=[0.5], colors='0.25', linewidths=0.25)
cs = ax.contour(srx, sry, si, levels=ut.pl.inlevs, colors='0.25', linewidths=0.1)
cs = ax.contour(srx, sry, si, levels=ut.pl.utlevs, colors='0.25', linewidths=0.25)

# add streamplot
print "plotting streamplot..."
ss = nc.streamplot('velsurf', ax, t, cmap='Blues', norm=ut.pl.velnorm,
                   density=(57, 30), linewidth=0.5, arrowsize=0.25)

# close extra data
nc.close()

# add colorbars
cb = ut.pl.add_colorbar(im, cax1, extend='both')
cb.set_label(r'topography (m) above sea (%.0f m)' % dsl)
cb = ut.pl.add_colorbar(ss.lines, cax2, extend='both')
cb.set_label(r'surface velocity ($m\,a^{-1}$)')

# add vector polygons
ut.ne.draw_natural_earth_color(ax)
ut.pl.draw_lgm_outline(ax)
ut.pl.draw_alpflo_ice_divides(ax)
ut.pl.draw_alpflo_water_divides(ax)

# add profiles
regions = ['thurn', 'engadin', 'simplon', 'mtcenis']
c = 'C9'
for i, reg in enumerate(regions):

    # read profile from shapefile
    filename = '../data/native/section_%s.shp' % reg
    shp = shpreader.Reader(filename)
    geom = shp.geometries().next()
    geom = geom[0]
    xp, yp = np.array(geom).T
    del shp, geom

    # compute distance along profile
    dp = (((xp[1:]-xp[:-1])**2+(yp[1:]-yp[:-1])**2)**0.5).cumsum()/1e3
    dp = np.insert(dp, 0, 0.0)

    # spline-interpolate profile
    di = np.arange(0.0, dp[-1], 0.5)
    xp = sinterp.spline(dp, xp, di)
    yp = sinterp.spline(dp, yp, di)
    dp = di

    # add profile line
    ax.plot(xp, yp, c=c, dashes=(2, 1))
    ax.plot(xp[[0, -1]], yp[[0, -1]], c=c, ls='', marker='o')

# add vector points and labels
ut.ne.draw_major_cities(ax, maxrank=12)
ut.pl.draw_alpflo_glacier_names(ax)
ut.pl.draw_alpflo_cross_divides(ax)
ut.pl.draw_alpflo_transfluences(ax)
#ut.pl.draw_alpflo_ice_domes(ax)
ut.pl.add_corner_tag('%.0f years ago' % -t, ax)

# save figure
print "saving figures..."
ut.pl.savefig()
