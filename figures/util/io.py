#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import iceplotlib.plot as iplt
import os

def load(filepath):
    """Load file relative to PISM directory."""

    filepath = os.path.join(os.environ['HOME'], 'pism', filepath)
    return iplt.load(filepath)
