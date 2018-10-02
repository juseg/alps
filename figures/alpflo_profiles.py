#!/usr/bin/env python
# coding: utf-8

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
import scipy.interpolate as sinterp

# parameters
regions = ['thurn', 'engadin', 'simplon', 'mtcenis']
nlabels = ['Alz', 'Rhine', '', 'Arc']
slabels = ['Tagliamento', 'Adda', 'Ticino', 'Dora Riparia']

# time for plot
t = -24530.0  # lgm -24533.6

# initialize figure
figw, figh = 400.0, 150.0
fig, grid = ut.mm.subplots_mm(nrows=4, ncols=1,
                              figsize=(figw, figh), sharex=True, sharey=True,
                              gridspec_kw=dict(left=10.0, right=2.5,
                                               bottom=10.0, top=2.5,
                                               hspace=0.0, wspace=0.0))
cax = fig.add_axes([22.5/figw, 22.5/figh, 60.0/figw, 5.0/figh])

# load extra data
filepath = ut.alpflo_bestrun + 'y0095480-extra.nc'
nc = ut.io.load(filepath)
x, y, b = nc._extract_xyz('topg', t)
x, y, s = nc._extract_xyz('usurf', t)
x, y, w = nc._extract_xyz('tempicethk_basal', t)
nc.close()

# load final data
filepath = ut.alpflo_bestrun + 'y0095480.nc'
nc = ut.io.load(filepath)
z = nc.variables['z'][:]/1e3
T = nc.variables['temp_pa'][0]
nc.close()

# load michael data
filepath = ('output/0.7.3/michael-wc-2km/2018_01_24__14_26_35_2km-'
            'rhine_slice_wcnn_100PDprecip_c12_ys-45000ye-15000_epica_'
            'siae3_ssae3_q0.5_tillphi30_dryra0.0_autotune_dT-8.1/ex.nc')
nc = ut.io.load(filepath)
xm, ym, s1 = nc._extract_xyz('usurf', t)
nc.close()
filepath = ('output/0.7.3/michael-wc-2km/2018_01_26__21_02_49_2km-'
            'rhine_slice_wcnn_100PDprecip_c12_ys-45000ye-15000_epica_'
            'siae3_ssae3_q0.5_tillphi10_dryra0.0_autotune_dT-9.2/ex.nc')
nc = ut.io.load(filepath)
xm, ym, s2 = nc._extract_xyz('usurf', t)
nc.close()
filepath = ('output/0.7.3/michael-wc-2km/2018_01_24__14_28_34_2km-'
            'rhine_slice_wcnn_15PDprecip_c12_ys-45000ye-15000_epica_'
            'siae3_ssae3_q0.5_tillphi30_dryra0.0_autotune_dT-13.8/ex.nc')
nc = ut.io.load(filepath)
xm, ym, s3 = nc._extract_xyz('usurf', t)
nc.close()

# loop on regions
for i, reg in enumerate(regions):
    ax = grid[i]

    # change spine visibility
    if i != 0:
        ax.spines['top'].set_color('none')
    if i != 3:
        ax.tick_params(axis='x', colors='none')
        ax.spines['bottom'].set_color('none')

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

    # extract space-time slice
    bp = sinterp.interpn((y, x), b, (yp, xp), method='linear')/1e3
    sp = sinterp.interpn((y, x), s, (yp, xp), method='linear')/1e3
    wp = sinterp.interpn((y, x), w, (yp, xp), method='linear')/1e3
    Tp = sinterp.interpn((y, x), T, (yp, xp), method='linear')

    # center on ice divide and fix orientation
    dp -= dp[sp.argmax()]
    dp *= np.sign(xp[-1]-xp[0])

    # create mesh grid and add basal topo
    dd, zz = np.meshgrid(dp, z)
    zz += bp[None, :]

    # set contour levels, colors and hatches
    levs = range(-18, 1, 3)
    cmap = plt.get_cmap('Blues_r', len(levs))
    cmap.set_over('C5')
    cols = cmap(range(len(levs)+1))

    # plot topographic profiles
    ax.plot(dp, bp.T, 'k-', lw=0.5)
    ax.plot(dp, sp.T, 'k-', lw=0.5)
    ax.plot(dp, (bp+wp).T, 'k-', lw=0.5)

    # plot Michael profiles
    if reg == 'engadin':
        sp1 = sinterp.interpn((ym, xm), s1, (yp, xp), method='linear')/1e3
        sp2 = sinterp.interpn((ym, xm), s2, (yp, xp), method='linear')/1e3
        sp3 = sinterp.interpn((ym, xm), s3, (yp, xp), method='linear')/1e3
        sp1 = np.ma.array(sp1, mask=dp>0.0)
        sp2 = np.ma.array(sp2, mask=dp>0.0)
        sp3 = np.ma.array(sp3, mask=dp>0.0)
        ax.plot(dp, sp1.T, 'k:', lw=0.5, label='100% precipitation')
        ax.plot(dp, sp3.T, 'k--', lw=0.5, label='15% precipitation')
        ax.plot(dp, sp2.T, 'k-.', lw=0.5, label=u'10° friction angle')

    # set mask above ice surface
    Tp = np.ma.array(Tp.T, mask=zz>sp[None, :])

    # plot temperature profile
    cs = ax.contourf(dd, zz, Tp, levels=levs, colors=cols, extend='both',
                     alpha=0.75)

    # plot temperate layer and frozen bed areas
    fp = np.ma.array(bp, mask=(Tp[0]>-1e-6)+(sp<bp+1e-3))
    ax.fill_between(dp, bp.T, (bp+wp).T, color=[cols[-1]], alpha=0.75,
                    label=('Temperate ice layer' if i == 3 else None))
    ax.fill_between(dp, fp.T-0.5, fp.T, hatch='////', facecolor='none',
                    label=('Cold-based areas' if i == 3 else None))

    # add age tag
    kw = dict(fontweight='bold', color='C1', ha='center')
    if nlabels[i] != '':
        ax.text(dp.min()+10.0, 1.5, nlabels[i] + ' Glacier', **kw)
    if slabels[i] != '':
        ax.text(dp.max()-10.0, 1.5, slabels[i] + ' Glacier', **kw)

    # add y label
    ax.set_ylabel('elevation (km)')
    ax.set_yticks(range(4))

# add colorbar
cb = fig.colorbar(cs, cax, orientation='horizontal')
cb.set_label(u'temperature below melting point (°C)')

# label glacier names
kw = dict(fontweight='bold', color='C1')
grid[2].text(-175.0, 2.0, 'Jura ice cap', **kw)
grid[2].text(-145.0, 2.0, 'Rhone Glacier', **kw)

# label ice divides
kw = dict(fontweight='bold', color='C7', ha='center')
grid[0].text(0.0, 3.25, 'Raneburg divide', **kw)
grid[1].text(0.0, 3.5, 'Engadin ice dome', **kw)
grid[2].text(0.0, 3.5, 'Gamsen divide', **kw)
grid[3].text(0.0, 3.5, 'Modane divide', **kw)

# label transfluences
kw = dict(fontweight='bold', color='C9', ha='center')
grid[0].text(-30.0, 0.0, 'Thurn Pass', **kw)
grid[0].text(-10.0, 0.0, 'Felber Tauern', **kw)
grid[0].text(55.0, 0.0, 'Gailberg Saddle', **kw)
grid[0].text(75.0, 0.0, u'Kronhofer Törl', **kw)
grid[1].text(-20.0, 0.0, 'Sertigpass', **kw)
grid[1].text(15.0, 0.0, 'Forcola di Livigno', **kw)
grid[2].text(25.0, 0.0, 'Geisspfad', **kw)
grid[3].text(20.0, 0.0, 'Col du Petit Mont-Cenis', **kw)

# set axes properties
ax.set_ylim(-0.25, 3.75)
ax.set_xlabel('distance from divide (km)')
grid[1].legend(loc='lower right', borderaxespad=2.0)
grid[3].legend(loc='lower right', borderaxespad=2.0)

# save
ut.pl.savefig()
