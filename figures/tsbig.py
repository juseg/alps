#!/usr/bin/env python2
# coding: utf-8

import util as ut

# time for LGM plot
lgm = 21.0

# Initialize figure
# -----------------

# initialize figure
fig, ax0 = ut.pl.subplots_mm(figsize=(250.0, 75.0),
                           left=15.0, right=30.0, bottom=15.0, top=20.0)
fig.patch.set_linewidth(1.0)

# prepare parasite axes
ax1 = ax0.twinx()
ax2 = ax0.twinx()
ax0.spines['left'].set_edgecolor('0.25')
ax1.spines['right'].set_edgecolor(ut.pl.palette['darkblue'])
ax2.spines['right'].set_edgecolor(ut.pl.palette['darkgreen'])
ax2.spines['right'].set_position(('axes', 1+15.0/205.0))
ax0.tick_params(axis='y', colors='0.25')
ax1.tick_params(axis='y', colors=ut.pl.palette['darkblue'])
ax2.tick_params(axis='y', colors=ut.pl.palette['darkgreen'])

# set bounds
ax0.set_xlim(120.0, 0.0)
ax0.set_ylim(-12.5, 7.5)
ax1.set_ylim(-0.05, 0.35)
ax2.set_ylim(-15.0, 25.0)

# limit ticks
ax0.locator_params(axis='y', nbins=6)
ax1.locator_params(axis='y', nbins=6)
ax2.locator_params(axis='y', nbins=6)

# add labels
ax0.set_xlabel('model age (ka)')
ax0.set_ylabel('temperature offset (K)', color='0.25')
ax1.set_ylabel('ice volume (m s.l.e.)', color=ut.pl.palette['darkblue'])
ax2.set_ylabel('uplift rate ($mm\,a^{-1}$)', color=ut.pl.palette['darkgreen'])

# add MIS stages
# source: http://www.lorraine-lisiecki.com/LR04_MISboundaries.txt
ax0.axvspan(71, 57, fc='0.9', lw=0.25, zorder=0)
ax0.axvspan(29, 14, fc='0.9', lw=0.25, zorder=0)
kwa = dict(ha='center', va='center')
ax0.text((120+71)/2, 6.0, 'MIS 5', **kwa)
ax0.text((71+57)/2, 6.0, 'MIS 4', **kwa)
ax0.text((57+29)/2, 6.0, 'MIS 3', **kwa)
ax0.text((29+14)/2, 6.0, 'MIS 2', **kwa)
ax0.text((14+0)/2, 6.0, 'MIS 1', **kwa)

# add grid and vertical line
ax0.grid(axis='y')
#ax0.axvline(lgm, c='k', lw=0.25)


# Time series
# -----------

# load dt forcing
nc = ut.io.load('input/dt/epica3222cool0950.nc')
age = -nc.variables['time'][:]/1e3
dt = nc.variables['delta_T'][:]
nc.close()

# plot temperature offset
ax0.plot(age, dt, c='0.25')

# load ts output
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/ts.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365*24*60*60)
vol = nc.variables['slvol'][:]
nc.close()

# plot ice volume
ax1.plot(age, vol, c=ut.pl.palette['darkblue'])
ax1.plot(lgm, vol[((age-lgm)**2).argmin()], 'o',
         ms=6, c='w', mec=ut.pl.palette['darkblue'], mew=1.0)

# load extra output
filepath = 'output/0.7.3/alps-wcnn-1km/epica3222cool0950+acyc1+esia5/extra.nc'
nc = ut.io.load(filepath)
age = -nc.variables['time'][:]/(1e3*365.0*24*60*60)
dbdt = nc.variables['dbdt'][:, 450, 350]*1e3
#print nc['x'][450], nc['y'][300]
#dbdt = nc.variables['dbdt'][:].mean(axis=(1, 2))*1e3
nc.close()

# plot central uplift rate
ax2.plot(age, dbdt, c=ut.pl.palette['darkgreen'])
ax2.plot(0.0, dbdt[-1], 'o',
         ms=6, c='w', mec=ut.pl.palette['darkgreen'], mew=1.0, clip_on=False)

# save figure
fig.savefig('tsbig')
