#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion time evolution."""

import os
import numpy as np
import xarray as xr
import matplotlib.colors as mcolors
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax, tsax) = apl.subplots_mm(figsize=(177, 119), nrows=2, sharex=True,
        gridspec_kw=dict(left=1.5+10, right=1.5+18, bottom=1.5+8, top=1.5,
                         hspace=4, height_ratios=(3, 1)))
    cax = fig.add_axes_mm([177-1.5-16, 1.5+38, 4, 78])

    # plot marine isotope stages
    util.fi.plot_mis(ax, y=None)
    util.fi.plot_mis(tsax, y=1.075)

    # load boot topography
    with xr.open_dataset(
            os.environ['HOME'] +
            '/pism/input/boot/alps.srtm.hus12.gou11simi.1km.nc'
            ) as boot:
        pass

    # load postprocessed data
    # FIXME postprocess erosion rates to avoid subsetting
    with util.io.open_mfdataset(
            os.environ['HOME'] +
            '/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.???????.nc',
            ) as ds:

        # subset
        ds = ds.sel(time=ds.time[99::100])

        # register erosion rate
        erosion = 2.7e-7*ds.velbase_mag.where(ds.thk >= 1)**2.02

        # group by elevation bins and compute geometric mean
        # FIXME if thk>0 but erosion=0 this is ignored in geometric mean
        erosion = np.exp(np.log(erosion.where(erosion > 0)).groupby_bins(
            boot.topg, bins=range(0, 4501, 100)).mean(axis=1))

        # plot
        erosion.assign_coords(age=ds.age/1e3).plot.imshow(
            ax=ax, x='age', cmap='YlOrBr', norm=mcolors.LogNorm(1e-9, 1e0),
            cbar_ax=cax, cbar_kwargs=dict(label=r'erosion rate ($m\,a^{-1}$)'))
        ax.set_xlabel('')
        ax.set_ylabel('elevation (m)')

    # load postprocessed data
    # FIXME add util to load erosion and volume series?
    with xr.open_mfdataset([
            '../data/processed/alpero.1km.epic.pp.agg.nc',
            '../data/processed/alpcyc.1km.epic.pp.ts.10a.nc'],
                           combine='by_coords', decode_cf=False,
                           join='override') as data:
        data = data[['slvol', 'erosion_rate']]
        data['age'] = -data.time/(365*24*60*60)
        data['rolling_mean'] = data.erosion_rate.rolling(
            time=100, center=True).mean()

        # plot ice volume time series
        tsax.plot(data.age/1e3, data.slvol*100, c='0.25')
        tsax.set_xlim(120.0, 0.0)
        tsax.set_xlabel('age (ka)')
        tsax.set_ylabel('ice volume (cm s.l.e.)')

        # plot erosion rate time series
        twax = tsax.twinx()
        twax.plot(data.age/1e3, data.erosion_rate*1e-9, c='C11', alpha=0.5)
        twax.plot(data.age/1e3, data.rolling_mean*1e-9, c='C11')
        twax.set_ylabel(r'erosion rate ($km^3\,a^{-1}$)', color='C11')
        twax.set_ylim(-0.5, 3.5)

    # save figure
    util.pl.savefig(fig)


if __name__ == '__main__':
    main()
