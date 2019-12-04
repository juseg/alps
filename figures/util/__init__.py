#!/usr/bin/env python2
# coding: utf-8

"""Utils and parameters for this project."""

import util.flo  # transfluences article
import util.geo  # mapping tools

import util.fi  # figure creation
import util.io  # input and output
import util.pl  # other plotting tools


# Alps cycle parameters
# ---------------------

alpcyc_records = ['GRIP']*2 + ['EPICA']*2 + ['MD01-2444']*2
alpcyc_configs = ['alpcyc4' + s for s in ['', '+pp']]*3
alpcyc_offsets = [7.0, 9.0, 8.8, 11.3, 7.3, 9.7]  # total area till1545 5km
alpcyc_offsets = [7.0, 9.0, 8.8, 11.4, 7.3, 9.8]  # total area till1545 2km
alpcyc_offsets = [8.3, 10.5, 9.8, 12.3, 8.2, 10.7]  # Rhine area till1545 5km
alpcyc_offsets = [8.2, 10.4, 9.5, 12.1, 8.1, 10.5]  # Rhine area phi30 5km
alpcyc_offsets = [8.2, 10.4, 9.7, 12.2, 8.0, 10.6]  # Rhine area phi30 2km
alpcyc_colours = ['C1', 'C0', 'C5', 'C4', 'C3', 'C2']  # db lb dr lr dg lg
alpcyc_colmaps = ['Blues_r']*2 + ['Reds_r']*2 + ['Greens_r']*2
alpcyc_clabels = [rec + ('pp' in conf)*', PP' for (rec, conf) in
                  zip(alpcyc_records, alpcyc_configs)]
alpcyc_bestrun = 'output/e9d2d1f/alpcyc4.1km.epica.1220.pp/'


# Alps flow parameters
# --------------------

alpflo_bestrun = 'output/1.1.3/alpcyc4.500m.epica.1220.pp/'
