#!/usr/bin/env python2
# coding: utf-8

"""Data processing methods."""

import os
import netCDF4 as nc4


# Alps cycle parameters
# ---------------------

alpcyc_bestrun = 'output/e9d2d1f/alps-wcnn-1km/epica3222cool1220+alpcyc4+pp'


def load(filepath):
    """Load file relative to PISM directory."""

    filepath = os.path.join(os.environ['HOME'], 'pism', filepath)
    return nc4.MFDataset(filepath)
