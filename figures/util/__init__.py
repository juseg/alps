# Copyright (c) 2016-2020, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Utils and parameters for the Alps project.
"""

import util.com  # common tools
import util.fig  # figure creation
import util.geo  # mapping tools

import util.cyc  # glacial cycle article
import util.ero  # glacier erosion article
import util.flo  # transfluences article


# Alps cycle parameters
# ---------------------

alpcyc_records = ['GRIP']*2 + ['EPICA']*2 + ['MD01-2444']*2
alpcyc_configs = ['alpcyc4' + s for s in ['', '.pp']]*3
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
