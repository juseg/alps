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
    fig, ax = apl.subplots_mm(figsize=(177, 119), gridspec_kw=dict(
        left=12, right=1.5, bottom=12, top=1.5))

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
        erosion = (2.7e-7*ds.velbase_mag**2.02).where(ds.thk >= 1.0)

        # group by elevation bins and compute geometric mean
        # FIXME if thk>0 but erosion=0 this is ignored in geometric mean
        erosion = np.exp(np.log(erosion.where(erosion > 0)).groupby_bins(
            boot.topg, bins=range(0, 4501, 100)).mean(axis=1))
    # plot
    erosion.assign_coords(age=ds.age/1e3).plot.imshow(
        ax=ax, x='age', cbar_kwargs=dict(label=r'erosion rate ($m\,a^{-1}$)'),
        cmap='YlOrBr', norm=mcolors.LogNorm())

    # set axes properties
    ax.set_xlim(120, 0)
    ax.set_xlabel('age (ka)')
    ax.set_ylabel('elevation (m)')

    # save figure
    util.pl.savefig(fig)


if __name__ == '__main__':
    main()
