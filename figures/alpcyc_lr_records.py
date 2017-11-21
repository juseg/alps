#!/usr/bin/env python2
# coding: utf-8

import util as ut
import numpy as np

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(45.0, 90.0), projection=ut.pl.stereo,
                            gridspec_kw=dict(left=2.5, right=2.5,
                                             bottom=2.5, top=2.5))
ax.set_rasterization_zorder(2.5)
ax.set_xlim(-15000e3, 15000e3)
ax.set_ylim(-36875e3, 26875e3)

# draw map elements
ax.gridlines(color='0.5', linestyle='-', linewidth=0.1)
ax.coastlines(edgecolor='k', lw=0.25)

# add modelling domain
w, e, s, n = 150e3, 1050e3, 4800e3, 5475e3
x = [w, w, e, e, w]
y = [s, n, n, s, s]
ax.plot(x, y, 'k', lw=1.0, transform=ut.pl.utm, zorder=3)

# add record locations
records = ['GRIP', 'EPICA', 'MD01-2444']
colors = ['darkblue', 'darkred', 'darkgreen']
colors = [ut.pl.palette[c] for c in colors]
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
