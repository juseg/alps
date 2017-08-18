#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.colors as mcolors

# initialize figure (one column)
figw, figh = 85.0, 115.0
fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
ax = fig.add_axes([2.5/figw, 2.5/figh, 80.0/figw, 80.0*2/3/figh], projection=ut.pl.utm)
cax = fig.add_axes([12.5/figw, (80.0*2/3-2.5)/figh, 30.0/figw, 2.5/figh])
scax = fig.add_axes([10.0/figw, 65.0/figh, 45.0/figw, 47.5/figh])
hsax = fig.add_axes([57.5/figw, 65.0/figh, 25.0/figw, 47.5/figh], sharey=scax)

## initialize figure (full width)
#figw, figh = 170.0, 60.0
#fig = ut.pl.figure(figsize=(figw/25.4, figh/25.4))
#ax = fig.add_axes([2.5/figw, 2.5/figh, 82.5/figw, 55.0/figh], projection=ut.pl.utm)
#cax = fig.add_axes([5.0/figw, 20.0/figh, 5.0/figw, 30.0/figh])
#scax = fig.add_axes([97.5/figw, 7.5/figh, 50.0/figw, 50.0/figh])
#hsax = fig.add_axes([150.0/figw, 7.5/figh, 17.5/figw, 50.0/figh], sharey=scax)

# prepare map axes
ax.set_rasterization_zorder(2.5)
ax.set_extent(ut.pl.regions['valais'], crs=ax.projection)

# add subfigure labels
ut.pl.add_subfig_label('(a)', ax=scax)
ut.pl.add_subfig_label('(b)', ax=hsax)
ut.pl.add_subfig_label('(c)', ax=ax)


# Input data
# ----------

# read trimlines data
trimlines = np.genfromtxt('../data/native/trimlines_kelly_etal_2004.csv',
                          dtype=None, delimiter=',', names=True)
xt = trimlines['x']
yt = trimlines['y']
zt = trimlines['z']

# convert to UTM 32
xt, yt, zt = ut.pl.utm.transform_points(ut.pl.swiss, xt, yt, zt).T

# read postprocessed data
envelope, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'envelope')
lgmtiming, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'lgmtiming')
maxicethk, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'maxicethk')
warmbased, extent = ut.io.load_postproc_gtif(ut.alpcyc_bestrun, 'warmbased')

# get coordinates  # FIXME not efficient
filepath = ut.alpcyc_bestrun + 'y0120000-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
nc.close()

# get model elevation at trimline locations
i = np.argmin(abs(xt[:, None] - x), axis=1)
j = np.argmin(abs(yt[:, None] - y), axis=1)
ht = maxicethk[-j-1, i]
at = lgmtiming[-j-1, i]/1e3


# Scatter axes
# ------------

# set contour levels and colors
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]
cmap, norm = mcolors.from_levels_and_colors(levs, cols, extend='both')

# draw scatter plot
sc = scax.scatter(zt, ht, c=at, cmap=cmap, norm=norm, alpha=0.75)
scax.set_xlabel('observed trimline elevation (m)')
scax.set_ylabel('modelled maximum ice thickness (m)', labelpad=2)


# Histogram axes
# --------------

# add histogram
step = 100.0
bmin = ht.min() - ht.min() % step
bmax = ht.max() - ht.max() % step + step
bins = np.arange(bmin, bmax+step, step)
hsax.hist(ht, bins=bins, orientation='horizontal', alpha=0.75)
hsax.set_xlabel('frequency')
[l.set_visible(False) for l in hsax.get_yticklabels()]

# highlight mean thickness
havg = ht.mean()
scax.axhline(havg, c='0.25')
hsax.axhline(havg, c='0.25')
hsax.text(2.0, havg+25.0, '%.0f m' % havg, color='0.25')

# Map axes
# --------

# plot areas with less than 1 ka warm ice cover
im = ax.contourf(warmbased, levels=[0e3, 1e3, 120e3], extent=extent,
                 colors=['w', 'w'], hatches=['////', ''], alpha=0.5)
cs = ax.contour(warmbased, [1e3], extent=extent, colors='0.25', linewidths=0.25)

# add ice mask and contour levels
ax.contourf(envelope.mask, levels=[-0.5, 0.5], extent=extent, colors='w', alpha=0.75)
ax.contour(envelope, ut.pl.inlevs, extent=extent, colors='0.25', linewidths=0.1)
ax.contour(envelope, ut.pl.utlevs, extent=extent, colors='0.25', linewidths=0.25)
ax.contour(envelope.mask, [0.5], extent=extent, colors='k', linewidths=0.5)

# draw trimlines
sc = ax.scatter(xt, yt, c=at, cmap=cmap, norm=norm, s=4**2, alpha=0.75)

# add map elements
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(sc, cax, orientation='horizontal')
cb.set_label(r'age (ka)')

# save figure
fig.savefig('alpcyc_hr_trimlines')
