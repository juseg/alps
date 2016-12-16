#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax, cax, tsax = ut.pl.subplots_cax_ts_cut(mis=False)


# Map axes
# --------

# load extra data
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
x = nc.variables['x'][:]
y = nc.variables['y'][:]
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
thk = nc.variables['thk'][:]
usurf = nc.variables['usurf'][:]

# compute LGM age and envelope
argmax = usurf.argmax(axis=0).T
lgmage = age[argmax]
cols, rows = usurf.shape[1:]
envelope = usurf[argmax, np.arange(cols)[None, :], np.arange(rows)[:, None]]

# apply thickness mask
mask = (thk < 1.0).prod(axis=0).T
lgmage = np.ma.masked_where(mask, lgmage)
envelope = np.ma.masked_where(mask, envelope)

# print bounds
#print 'LGM age min %.1f, max %.1f' % (lgmage.min(), lgmage.max())

# set contour levels, colors and hatches
levs = range(21, 28)
cmap = ut.pl.get_cmap('Paired', 12)
cols = cmap(range(12))[:len(levs)+1]

# plot
im = nc.imshow('topg', ax, 0.0, vmin=0.0, vmax=3e3, cmap='Greys', zorder=-1)
cs = ax.contourf(x, y, lgmage, levs, colors=cols, extend='both', alpha=0.75)

# contour levels
ax.contour(x, y, envelope, ut.pl.inlevs, colors='0.25', linewidths=0.1)
ax.contour(x, y, envelope, ut.pl.utlevs, colors='0.25', linewidths=0.25)

# ice margin
ax.contour(x, y, mask, [0.5], colors='k', linewidths=0.5)

# close nc file
nc.close()

# add cartopy vectors
ut.pl.draw_natural_earth(ax)

# add colorbar
cb = fig.colorbar(cs, cax)
cb.set_label(r'age of maximum ice surface elevation (ka)')


# Time series
# -----------

# compute glaciated areas in 1e3 km2
dx = x[1] - x[0]
dy = y[1] - y[0]
area = (thk >= 1.0).sum(axis=(1, 2))*dx*dy*1e-9

# plot time series
twax = tsax.twinx()
for i, c in enumerate(cols):
    agemax = (120 if i == len(levs) else levs[i])
    agemin = (0 if i == 0 else levs[i-1])
    idxmin = np.argmin(abs(age-agemax))
    idxmax = np.argmin(abs(age-agemin))
    twax.plot(age[idxmin:idxmax+1], area[idxmin:idxmax+1], c=c, lw=2.0)
twax.set_ylabel(r'glaciated area ($10^3\,km^2$)',
                color=ut.pl.palette['darkblue'])
twax.set_xlim(29.0, 17.0)
twax.set_ylim(90.0, 170.0)
twax.locator_params(axis='y', nbins=6)

# save figure
fig.savefig('timing')
