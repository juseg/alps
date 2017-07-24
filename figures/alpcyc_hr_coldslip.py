#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax = ut.pl.subplots_ts()
ax.set_rasterization_zorder(2.5)

# time for plot
a = 24.57
t = -a*1e3

# load extra data
filepath = ut.alpcyc_bestrun + 'y???????-extra.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
idx = ((age-a)**2).argmin()
tem = nc.variables['temppabase'][idx]
thk = nc.variables['thk'][idx]
vel = nc.variables['velbase_mag'][idx]
nc.close()

# mask ice-free cells
mask = (thk < 1.0)
tem = np.ma.masked_where(mask, tem)
thk = np.ma.masked_where(mask, thk)
vel = np.ma.masked_where(mask, vel)

# compute color mask for problem area
cols = (tem < -1e-3) * (vel > 1e1)
print cols.sum()
cmap = ut.pl.iplt.matplotlib.colors.ListedColormap([ut.pl.palette['darkblue'],
                                                    ut.pl.palette['darkred']])

# plot
ax.set_xscale('symlog', linthreshx=1e-6)
ax.set_yscale('log')
ax.set_xlabel('basal temperature (K)')
ax.set_ylabel('basal velocity ($m\,a^{-1}$)')
ax.scatter(tem, vel, c=cols, cmap=cmap, alpha=0.1)

# save figure
fig.savefig('alpcyc_hr_coldslip')
