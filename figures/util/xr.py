# Copyright (c) 2018, Julien Seguinot <seguinot@vaw.baug.ethz.ch>

"""Xarray dataarrays and dataset computations."""

import numpy as np
import xarray as xr


def gradient(darray):
    """Compute gradient along a all dimensions of a data array."""

    # extract coordinate data
    dims = darray.dims
    coords = [darray[d].data for d in dims]

    # apply numpy.gradient
    darray = xr.apply_ufunc(np.gradient, darray, *coords,
                            input_core_dims=(dims,)+dims,
                            output_core_dims=[('n',)+dims])

    # add vector component coordinate
    darray = darray.assign_coords(n=list(dims))

    # return as single dataarray
    return darray


def shading(darray, azimuth=315.0, altitude=30.0, transparent=False):
    """Compute shaded relief map from a data array."""

    # convert to rad
    azimuth *= np.pi / 180.
    altitude *= np.pi / 180.

    # compute cartesian coords of the illumination direction
    # for transparent shades set horizontal surfaces to zero
    xlight = np.sin(azimuth) * np.cos(altitude)
    ylight = np.cos(azimuth) * np.cos(altitude)
    zlight = (0.0 if transparent else np.sin(altitude))

    # compute hillshade (minus dot product of normal and light direction)
    v, u = gradient(darray)
    shade = - (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)
    return shade


def multishading(darray):
    """Compute shaded relief using multiple light sources."""

    # compute relief shading
    s300 = shading(darray, azimuth=300.0, altitude=30.0, transparent=True)
    s315 = shading(darray, azimuth=315.0, altitude=30.0, transparent=True)
    s330 = shading(darray, azimuth=330.0, altitude=30.0, transparent=True)
    return (s300+2.0*s315+s330)/4.0
