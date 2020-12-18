#!/usr/bin/env python
# Copyright (c) 2019-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion hypsogram."""

import os
import numpy as np
import xarray as xr
import matplotlib.colors as mcolors
import absplots as apl
import pismx.open
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax, tsax) = apl.subplots_mm(
        figsize=(177, 119), nrows=2, sharex=True, gridspec_kw=dict(
            left=1.5+10, right=1.5+18, bottom=1.5+8, top=1.5,
            hspace=4, height_ratios=(3, 1)))
    cax = fig.add_axes_mm([177-1.5-16, 1.5+38, 4, 78])

    # plot time series
    util.fig.plot_mis(ax, y=None)
    util.fig.plot_mis(tsax, y=1.075)
    util.ero.plot_series(ax=tsax)

    # load boot topography
    with xr.open_dataset(
            os.environ['HOME'] +
            '/pism/input/boot/alps.srtm.hus12.gou11simi.1km.nc'
            ) as boot:
        pass

    # load postprocessed data
    # FIXME postprocess erosion rates to avoid subsetting
    with pismx.open.mfdataset(
            os.environ['HOME'] +
            '/pism/output/e9d2d1f/alpcyc4.1km.epica.1220.pp/ex.???????.nc',
            ) as ds:

        # subset
        ds = ds.sel(age=ds.age[99::100])

        # register erosion rate
        erosion = 2.7e-7*ds.velbase_mag.where(ds.thk >= 1)**2.02

        # group by elevation bins and compute geometric mean
        # FIXME if thk>0 but erosion=0 this is ignored in geometric mean
        erosion = np.exp(np.log(erosion.where(erosion > 0)).groupby_bins(
            boot.topg, bins=range(0, 4501, 100)).mean(axis=1))

        # plot
        erosion.assign_coords(age=ds.age).plot.imshow(
            ax=ax, x='age', cmap='YlOrBr', norm=mcolors.LogNorm(1e-9, 1e0),
            cbar_ax=cax, cbar_kwargs=dict(label=r'erosion rate ($m\,a^{-1}$)'))
        ax.set_xlabel('')
        ax.set_ylabel('elevation (m)')
        ax.set_xlim(120, 0)

    # save figure
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
