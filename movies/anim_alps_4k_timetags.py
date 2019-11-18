#!/usr/bin/env python
# Copyright (c) 2018-2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import os
import yaml
import multiprocessing as mp
import matplotlib.pyplot as plt
import utils as ut

"""Plot Alps 4k animations time tag overlays."""


def timetag(t, lang='en'):
    """Plot time tag overlay for given time."""

    # initialize figure
    figw, figh = 32.0, 6.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))

    # import language-dependent label
    with open('anim_alps_4k_zo_{}.yaml'.format(lang)) as f:
        tag = yaml.safe_load(f)['Labels'][0].format(0-t)
    if lang != 'ja':
        tag = tag.replace(',', r'$\,$')
    fig.text(2.5/figw, 1-2.5/figh, tag, ha='left', va='top', fontweight='bold')

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'zo'])
    parser.add_argument('lang', choices=['de', 'en', 'fr', 'it', 'ja', 'nl'])
    args = parser.parse_args()

    # set default font properties
    plt.rc('savefig', dpi=508, facecolor='none')
    plt.rc('axes', facecolor='none')
    if args.lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # start and end of animation
    if args.crop in ('lu', 'ma'):
        t0, t1, dt = -45000, -15000, 10
    else:
        t0, t1, dt = -120000, -0, 10000

    # output frame directories
    outdir = os.path.join(
        os.environ['HOME'], 'anim', 'anim_alps_4k',
        '_ttag_'+args.lang+'_'+'{:.0f}{:.0f}'.format(-t0/1e3, -t1/1e3))

    # iterable arguments to save animation frames
    iter_args = [(timetag, outdir, t, args.lang)
                 for t in range(t0+dt, t1+1, dt)]

    # create frames directory if missing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
