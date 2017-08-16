#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut(mis=False)


# Map axes
# --------

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
thk = nc.variables['thk'][:]
usurf = nc.variables['usurf'][:]

# compute LGM age and envelope
argmax = usurf.argmax(axis=0)
lgmage = age[argmax]
cols, rows = usurf.shape[1:]
envelope = usurf[argmax, np.arange(cols)[:, None], np.arange(rows)[None, :]]

# apply thickness mask
mask = (thk < 1.0).prod(axis=0)
lgmage = np.ma.masked_where(mask, lgmage)
envelope = np.ma.masked_where(mask, envelope)

# set contour levels, colors and hatches
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]

# plot
cs = ax.contourf(x, y, lgmage, levs, colors=cols, extend='both', alpha=0.75)

# contour levels
ax.contour(x, y, envelope, ut.pl.inlevs, colors='0.25', linewidths=0.1)
ax.contour(x, y, envelope, ut.pl.utlevs, colors='0.25', linewidths=0.25)

# ice margin
ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ut.pl.draw_boot_topo(ax)
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'age of maximum ice surface elevation (ka)')


# Time series
# -----------

# load time series
filepath = ut.alpcyc_bestrun + 'y???????-ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
area = nc.variables['area_glacierized'][:]*1e-9
nc.close()

# print age of max area
#print age[area.argmax()]

# plot time series
twax = tsax.twinx()
ut.pl.plot_multicolor(age, area, levs[::-1], cols[::-1], ax=twax)
twax.set_ylabel(r'glaciated area ($10^3\,km^2$)',
                color=ut.pl.palette['darkblue'])
twax.set_xlim(29.0, 17.0)
twax.set_ylim(90.0, 170.0)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('alpcyc_hr_timing')
