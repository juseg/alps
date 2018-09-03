#!/usr/bin/env python2
# coding: utf-8

import util as ut
import matplotlib.transforms as mtrans
from mpl_toolkits.axes_grid1.inset_locator import BboxPatch, BboxConnector, BboxConnectorPatch

# parameters
c = 'C1'
versions = ['e9d2d1f', '1.0']
resolutions = ['1km', '500m']
linestyles = ['-', ':']

# initialize time-series figure
figw, figh = 225.0, 125.0
fig, grid = ut.mm.subplots_mm(nrows=2, ncols=1, figsize=(figw, figh),
                              sharex=False, sharey=True,
                              gridspec_kw=dict(left=10.0, right=10.0,
                                               bottom=10.0, top=2.5,
                                               hspace=2.5, wspace=2.5))
ut.pl.add_subfig_label('(a)', ax=grid[0], y=0.75)
ut.pl.add_subfig_label('(b)', ax=grid[1])
twgrid = [ax.twinx() for ax in grid]

# plot temperature time series
dtfile = 'epica3222cool1220'
for ax in grid:
    ut.pl.plot_dt(ax=ax)

# for each resolution
for i, res in enumerate(resolutions):
    ver = versions[i]
    ls = linestyles[i]

    # load output time series
    runname = 'output/%s/alps-wcnn-%s/%s+alpcyc4+pp/' % (ver, res, dtfile)
    filepath = runname + 'y???????-ts.nc'
    nc = ut.io.load(filepath)
    age = -nc.variables['time'][::12]/(1e3*365*24*60*60)
    vol = nc.variables['slvol'][::12]*100.0
    nc.close()

    # print LGM age
    #print age[vol.argmax()]

    # plot time series
    for ax in twgrid:
        ax.plot(age, vol, c=c, ls=ls, label=res)

# set axes properties
grid[0].set_xlim(120.0, 0.0)  # no need
grid[1].set_xlim(32.5, 22.5)
grid[1].set_ylim(-16.25, 1.25)
twgrid[0].set_ylim(-2.5, 32.5)
twgrid[1].set_ylim(-2.5, 32.5)
twgrid[0].set_ylabel('ice volume (cm s.l.e.)')
twgrid[1].set_ylabel('ice volume (cm s.l.e.)')
ax.legend()

# mark simulation span
trans1 = mtrans.blended_transform_factory(grid[0].transData, grid[0].transAxes)
trans2 = mtrans.blended_transform_factory(grid[1].transData, grid[1].transAxes)
bbox0 = mtrans.Bbox.from_extents(25.0, 0, 24.5, 1)
bbox1 = mtrans.TransformedBbox(bbox0, trans1)
bbox2 = mtrans.TransformedBbox(bbox0, trans2)
p1 = BboxPatch(bbox1, fc='0.9')
p2 = BboxPatch(bbox2, fc='0.9')
p0 = BboxConnectorPatch(bbox1, bbox2,
                        loc1a=3, loc2a=2, loc1b=4, loc2b=1, fc='0.9')
p0.set_fill(True)  # will be fixed in matplotlib v3.0
p0.set_clip_on(False)
grid[0].add_patch(p0)
grid[0].add_patch(p1)
grid[1].add_patch(p2)

# mark zoom inset
trans1 = mtrans.blended_transform_factory(grid[0].transData, grid[0].transAxes)
trans2 = mtrans.blended_transform_factory(grid[1].transData, grid[1].transAxes)
x0, x1 = grid[1].get_xlim()
bbox0 = mtrans.Bbox.from_extents(x0, 0, x1, 1)
bbox1 = mtrans.TransformedBbox(bbox0, trans1)
bbox2 = mtrans.TransformedBbox(bbox0, trans2)
p1 = BboxPatch(bbox1, fc='none', ec='0.5', ls='--')
p2 = BboxPatch(bbox2, fc='none', ec='0.5', ls='--')
c0 = BboxConnector(bbox1, bbox2, loc1=4, loc2=1, ec='0.5', ls='--')
c1 = BboxConnector(bbox1, bbox2, loc1=3, loc2=2, ec='0.5', ls='--')
c0.set_clip_on(False)
c1.set_clip_on(False)
grid[0].add_patch(c0)
grid[0].add_patch(c1)
grid[0].add_patch(p1)
grid[1].add_patch(p2)

# save
ut.pl.savefig()
