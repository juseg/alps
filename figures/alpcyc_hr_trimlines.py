#!/usr/bin/env python
# Copyright (c) 2016-2022, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import pandas as pd
import hyoga.open
import util
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs

utm = ccrs.UTM(32)
swiss = ccrs.TransverseMercator(
    central_longitude=7.439583333333333, central_latitude=46.95240555555556,
    false_easting=600e3, false_northing=200e3, approx=False)


def open_trimline_data():
    """Open trimline dataset."""

    # read trimlines data
    ds = pd.read_csv('../data/native/trimlines_kelly_etal_2004.csv',
                     index_col='id').to_xarray()

    # convert to UTM 32
    xyz = utm.transform_points(swiss, ds.x.data, ds.y.data, ds.z.data).T
    ds['x'].data, ds['y'].data, ds['z'].data = xyz

    # return dataset
    return ds


# initialize figure
fig, ax, cax, scax, hsax = util.fig.subplots_trimlines()


# Input data
# ----------

# load trimlines data in memory
with open_trimline_data() as tr:
    tr.load()

# get aggregated data at trimline locations
with hyoga.open.dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    at = ds.maxthkage.interp(x=tr.x, y=tr.y, method='linear')/1e3
    ht = ds.maxthkthk.interp(x=tr.x, y=tr.y, method='linear')

# get boot topography at trimline locations
with hyoga.open.dataset('../data/processed/alpcyc.1km.in.nc') as ds:
    bt = ds.topg.interp(x=tr.x, y=tr.y, method='linear')


# Scatter axes
# ------------

# age levels and colors
levs = range(21, 28)
cols = plt.get_cmap('Paired').colors[:len(levs)+1]
cmap, norm = mcolors.from_levels_and_colors(levs, cols, extend='both')

# draw scatter plot
sc = scax.scatter(tr.z, bt+ht, c=at, cmap=cmap, norm=norm, alpha=0.75)
scax.set_xlabel('observed trimline elevation (m)')
scax.set_ylabel('compensated LGM surface elevation (m)')


# Histogram axes
# --------------

# diff between compensated surface elevation and trimlines
dt = bt + ht - tr.z

# add histogram
step = 100
bmin = int(dt.min() - dt.min() % step)
bmax = int(dt.max() - dt.max() % step + step)
bins = range(bmin, bmax+1, step)
hsax.hist(dt, bins=bins, color='C1', orientation='horizontal', alpha=0.75)
hsax.set_xlabel('frequency')
hsax.set_ylabel('difference (m)')
hsax.yaxis.set_label_position("right")
hsax.yaxis.tick_right()

# highlight mean difference
zavg = tr.z.mean()
davg = dt.mean()
dstd = dt.std()
zz = tr.z[[tr.z.argmin(), tr.z.argmax()]]
scax.plot(zz, zz+davg, c='0.25')
scax.plot(zz, zz+davg-dstd, c='0.25', dashes=(2, 1), lw=0.5)
scax.plot(zz, zz+davg+dstd, c='0.25', dashes=(2, 1), lw=0.5)
scax.axvline(zavg, c='0.25', dashes=(2, 1), lw=0.5)
scax.axhline(zavg+davg, c='0.25', dashes=(2, 1), lw=0.5)
scax.text(zavg-25.0, (bt+ht).min(), '%.0f m' % zavg, color='0.25',
          rotation=90, rotation_mode='anchor')
scax.text(zz[0], zavg+davg+25.0, '%.0f m' % (zavg+davg), color='0.25')
hsax.axhline(davg, c='0.25')
hsax.axhline(davg-dstd, c='0.25', dashes=(2, 1), lw=0.5)
hsax.axhline(davg+dstd, c='0.25', dashes=(2, 1), lw=0.5)
hsax.text(2.0, davg+25.0, '%.0f m' % davg, color='0.25')

# align axes bounds
hsax.set_ylim(l-zavg for l in scax.get_ylim())


# Map axes
# --------

# load aggregated data
with hyoga.open.dataset('../data/processed/alpcyc.1km.epic.pp.agg.nc') as ds:
    btp = ds.maxthkbtp
    srf = ds.maxthksrf
    ext = ds.maxthksrf.notnull()

    # plot cold-based areas at max thickness age
    btp.plot.contourf(ax=ax, add_colorbar=False, alpha=0.5, colors=['w']*2,
                      hatches=['////', ''], levels=[-50.0, -1e-3, 0.0])
    btp.plot.contour(ax=ax, colors='0.25', levels=[-1e-3],
                     linestyles='-', linewidths=0.25)
    srf.plot.contour(ax=ax, colors='0.25', levels=util.com.inlevs,
                     linewidths=0.1)
    srf.plot.contour(ax=ax, colors='0.25', levels=util.com.utlevs,
                     linewidths=0.25)
    ext.plot.contourf(ax=ax, add_colorbar=False, alpha=0.75, colors='w',
                      extend='neither', levels=[0.5, 1.5])
    ext.plot.contour(ax=ax, colors='k', levels=[0.5], linewidths=0.25)

# remove xarray auto title
ax.set_title('')

# add map elements
util.geo.draw_boot_topo(ax)
util.geo.draw_natural_earth(ax)

# add text labels
kw = dict(ha='center', va='center', transform=ccrs.PlateCarree())
ax.text(6.865, 45.834, 'Mont\nBlanc', **kw)
ax.text(7.659, 45.976, 'Matter-\nhorn', **kw)
ax.text(7.867, 45.937, 'Monte\nRosa', **kw)
ax.text(7.963, 46.537, 'Jungfrau', **kw)
#ax.text(8.126, 46.537, 'Finsternaarhorn', **kw)
ax.text(7.367, 46.233, 'Rhone', rotation=30, **kw)

# draw trimlines
sc = ax.scatter(tr.x, tr.y, c=at, cmap=cmap, norm=norm, s=4**2, alpha=0.75)

# add colorbar
cb = util.com.add_colorbar(sc, cax)
cb.set_label(r'age (ka)')

# save figure
util.com.savefig()
