#!/usr/bin/env python
# Copyright (c) 2018-2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import os
import multiprocessing as mp
import matplotlib.pyplot as plt
import utils as ut

"""Plot Alps 4k animations city map overlays."""


def plot(t, crop='al', lang='en', t0=-120e3, t1=0e3):
    """Plot city map overlay for given time."""

    # initialize figure
    fig, ax = ut.axes_anim_dynamic(crop=crop, t=t, t0=t0, t1=t1,
                                   figsize=(192.0, 108.0))

    # draw map elements
    # FIXME move cities to cartowik?
    ut.draw_major_cities(ax=ax, exclude='Monaco', include='Sion', lang=lang,
                         maxrank=(8 if crop in ('lu', 'ma') else 6))

    # return figure
    return fig


def main():
    """Main program for command-line execution."""

    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('crop', choices=['al', 'ch', 'lu', 'ma', 'ul', 'zo'])
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

    # output frames directory
    outdir = os.path.join(
        os.environ['HOME'], 'anim', 'anim_alps_4k_city_{}_{}'.format(
            args.crop, args.lang))

    # range of frames to save
    time_range = [t1] if args.crop in ('al', 'ul') else range(t0+dt, t1+1, dt)

    # iterable arguments to save animation frames
    iter_args = [(plot, outdir, t, args.crop, args.lang, t0, t1)
                 for t in time_range]

    # create frame directories if missing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # plot all frames in parallel
    with mp.Pool(processes=4) as pool:
        pool.starmap(ut.save_animation_frame, iter_args)


if __name__ == '__main__':
    main()
