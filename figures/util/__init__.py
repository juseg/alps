#!/usr/bin/env python2
# coding: utf-8

"""Utils and parameters for this project."""

# append submodule paths
#import sys
#sys.path.append('iceplotlib')

import io
import pl
import matplotlib.pyplot as plt

# build color brewer Paired palette
colorkeys = [tone+hue
             for hue in ('blue', 'green', 'red', 'orange', 'purple', 'brown')
             for tone in ('light', 'dark')]
colorvals = plt.get_cmap('Paired', 12)(range(12))
palette = dict(zip(colorkeys, colorvals))