#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
figw, figh = 170.0, 97.5
fig, grid = ut.pl.subplots_mm(figsize=(figw, figh), projection=ut.pl.utm,
                             nrows=2, ncols=2, sharex=True, sharey=True,
                             left=2.5, right=15.0, bottom=2.5, top=2.5,
                             hspace=2.5, wspace=17.5)
cgrid = [fig.add_axes([(72.5+i*85.0)/figw, (50.0-j*47.5)/figh, 2.5/figw, 45.0/figh])
         for j in range(2) for i in range(2)]

# add map elements
for i, ax in enumerate(grid.flat):
    ax.set_rasterization_zorder(2.5)
    ut.pl.draw_boot_topo(ax)
    ut.pl.draw_natural_earth(ax)
    ut.pl.add_subfig_label('(%s)' % list('abcd')[i], ax)

# plot boot geoflux on last panel
nc = ut.io.load('input/boot/alps-srtm+thk+gou11simi-1km.nc')
ax = grid.flat[3]
cax = cgrid[3]
levs = range(55, 96, 5)
cmap = ut.pl.get_cmap('PuOr_r', len(levs)-1)
cols = cmap(range(len(levs)-1))
cs = nc.contourf('bheatflx', ax, levels=levs, colors=cols, thkth=-1, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='vertical', ticks=levs[1::2])
cb.set_label(r'Geothermal flux ($mW\,m^{-2}$)')
nc.close()

# load atm file
# FIXME: add unit conversion to iceplotlib
nc = ut.io.load('input/atm/alps-wcnn-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
temp = nc.variables['air_temp'][6].T-273.15
prec = nc.variables['precipitation'][0].T*910.0/12
nc.close()

# load standard deviation file
# FIXME: add unit conversion to iceplotlib
nc = ut.io.load('input/sd/alps-erai-1km.nc')
x = nc.variables['x'][:]
y = nc.variables['y'][:]
sd = nc.variables['air_temp_sd'][6].T
nc.close()

# plot July temperature
#print 'July temp min %.1f, max %.1f' % (temp.min(), temp[3:-3, 3:-3].max())
ax = grid.flat[0]
cax = cgrid[0]
levs = range(-5, 26, 5)
cmap = ut.pl.get_cmap('RdBu_r', len(levs)-1)
cols = cmap(range(len(levs)))
cs = ax.contourf(x, y, temp, levs, colors=cols, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='vertical', ticks=levs[1::2])
cb.set_label(u'July temperature (°C)')

# plot January precipitation
#print 'Jan. prec min %.1f, max %.1f' % (prec.min(), prec.max())
ax = grid.flat[1]
cax = cgrid[1]
levs = range(0, 301, 50)
cmap = ut.pl.get_cmap('Greens', len(levs)-1)
cols = cmap(range(len(levs)))
cs = ax.contourf(x, y, prec, levs, colors=cols, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='vertical', ticks=levs[::2])
cb.set_label(r'January precipitation (mm)')

# plot July standard deviation
#print 'July s.d. min %.1f, max %.1f' % (sd.min(), sd.max())
ax = grid.flat[2]
cax = cgrid[2]
levs = [1.7, 2.0, 2.3, 2.6, 2.9, 3.2, 3.5]
cmap = ut.pl.get_cmap('Reds', len(levs)-1)
cols = cmap(range(len(levs)-1))
cs = ax.contourf(x, y, sd, levs, colors=cols, alpha=0.75)
cb = fig.colorbar(cs, cax, orientation='vertical', ticks=levs[1::2])
cb.set_label(u'July PDD SD (°C)')

# save
fig.savefig('alpcyc_hr_inputs')
