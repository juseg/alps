#!/usr/bin/env python
# Copyright (c) 2017--2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps transfluence poster map."""

# import cartopy.io.shapereader as shpreader
# import scipy.interpolate as sinterp
import cartopy.crs as ccrs
import cartowik.conventions as ccv
import cartowik.decorations as cde
import cartowik.naturalearth as cne
import cartowik.profiletools as cpf
import cartowik.shadedrelief as csr
import pandas as pd
import absplots as apl
import hyoga
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(900, 600), dpi=254)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.UTM(32))
    cax1 = fig.add_axes([20/900, 40/600, 50/900, 5/600])
    cax2 = fig.add_axes([20/900, 60/600, 50/900, 5/600])
    ax.spines['geo'].set_edgecolor('none')
    util.fig.prepare_map_axes(ax, extent='alps')

    # target LGM age
    lgmage = 24.611

    # estimate sea level drop
    dsl = pd.read_csv('../data/external/spratt2016.txt', comment='#',
                      delimiter='\t', index_col='age_calkaBP').to_xarray()
    dsl = dsl.SeaLev_shortPC1.dropna('age_calkaBP')
    dsl = min(dsl.interp(age_calkaBP=lgmage, method='cubic').values, 0.0)

    # load extra data
    filename = '~/pism/output/1.1.3/alpflo1.500m.epica.1220.pp/ex.0095390.nc'
    with hyoga.open.dataset(filename) as ds:
        ds = ds.sel(age=lgmage)
        ds = ds[['lon', 'lat', 'topg', 'thk', 'usurf', 'uvelsurf', 'vvelsurf']]

        # compute isostasy and interpolate
        ds = ds.hyoga.assign_isostasy(
            '~/pism/input/boot/alps.srtm.hus12.gou11simi.500m.nc')
        interp = ds.hyoga.interp(
            '~/pism/input/boot/alps.srtm.hus12.200m.nc')

        # plot interpolated output
        # FIXME default to add_colorbar=True if cbar_ax is present in hyoga
        interp.hyoga.plot.bedrock_altitude(
            cmap=ccv.ELEVATIONAL, vmin=-4500, vmax=4500, ax=ax, sealevel=dsl,
            add_colorbar=True, cbar_ax=cax1, cbar_kwargs=dict(
                orientation='horizontal', label=(
                    'bedrock altitude (m) above sea level '
                    '({:.0f} m)'.format(dsl))))
        interp.hyoga.plot.bedrock_shoreline(
            colors='#0978ab', ax=ax, sealevel=dsl)
        csr.add_multishade(interp.topg, ax=ax, add_colorbar=False, zorder=-1)
        interp.hyoga.plot.surface_altitude_contours(ax=ax)
        interp.hyoga.plot.ice_margin(ax=ax, facecolor='w', alpha=0.75)
        interp.hyoga.plot.ice_margin(ax=ax, edgecolor='0.25')

        # add surface streamplot
        ds = ds.hyoga.where_thicker(1)
        streams = ds.hyoga.plot.surface_velocity_streamplot(
            ax=ax, cmap='Blues', vmin=1e1, vmax=1e3, density=(24, 16))
        fig.colorbar(
                streams.lines, cax=cax2, extend='both',
                orientation='horizontal',
                label=r'ice surface velocity ($m\,a^{-1}$)')

    # save background map
    fig.savefig(__file__[:-3]+'_bg.png')

    # add map elements
    util.geo.draw_natural_earth(ax, mode='co')
    util.geo.draw_lgm_outline(ax)
    util.flo.draw_ice_divides(ax)
    util.flo.draw_water_divides(ax)
    cde.add_scale_bar(ax, label='50 km', length=50e3)

    # add profiles
    for section in ['thurn', 'engadin', 'simplon', 'mtcenis']:
        filename = '../data/native/section_{}.shp'.format(section)
        x, y = cpf.read_shp_coords(filename)
        ax.plot(x, y, color='C9', dashes=(2, 1))
        ax.plot(x[[0, -1]], y[[0, -1]], color='C9', ls='', marker='o')

    # add vector points and labels
    cne.add_cities(ax=ax, color='0.25', marker='o', s=6, exclude=['Monaco'],
                   ranks=range(12))
    util.flo.draw_glacier_names(ax)
    util.flo.draw_cross_divides(ax)
    util.flo.draw_transfluences(ax)
    util.com.add_corner_tag('{:.0f} years ago'.format(lgmage*1e3), ax=ax)

    # save figure
    fig.savefig(__file__[:-3]+'.png')
    fig.savefig(__file__[:-3]+'.pdf')


if __name__ == '__main__':
    main()
