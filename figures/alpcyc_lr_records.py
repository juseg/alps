#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np
import iceplotlib.plot as iplt
import cartopy.crs as ccrs

# initialize figure
proj = ccrs.Stereographic(central_latitude=-10.0, central_longitude=10.0)
fig, ax = iplt.subplots_mm(figsize=(45.0, 90.0), projection=proj,
                           gridspec_kw=dict(left=0.0, right=0.0,
                                            bottom=0.0, top=0.0))
ax.set_rasterization_zorder(2.5)
ax.set_xlim(-7500e3, 7500e3)
ax.set_ylim(-15000e3, 15000e3)

# draw map elements
ax.gridlines(color='0.5', linestyle='-', linewidth=0.1)
ax.coastlines(edgecolor='k', lw=0.25)

# add modelling domain
ut.pl.draw_model_domain(ax=ax, extent='alps')

# add record locations
records = ['GRIP', 'EPICA', 'MD01-2444']
colors = ['C1', 'C5', 'C3']
lats = np.array([72.58, -75.1, 37.561])
lons = np.array([-37.64, 123.35, -10.142])
locs = ['uc', 'uc', 'lc']
x, y, _ = ax.projection.transform_points(ut.pl.ll, lons, lats).T
ax.scatter(lons, lats, c=colors, linewidths=0.25, transform=ut.pl.ll)

# add record labels
offset = 6
for i, rec in enumerate(records):
    xy = x[i], y[i]
    loc = locs[i]
    xoffset = ((loc[1] == 'r')-(loc[1] == 'l')) * offset
    yoffset = ((loc[0] == 'u')-(loc[0] == 'l')) * offset
    xytext = xoffset, yoffset
    ha={'r': 'left', 'l': 'right', 'c': 'center'}[loc[1]]
    va={'u': 'bottom', 'l': 'top', 'c': 'center'}[loc[0]]
    ax.annotate(rec, xy=xy, xytext=xytext, ha=ha, va=va, color=colors[i],
                textcoords='offset points', fontweight='bold')

# save
ut.pl.savefig()
