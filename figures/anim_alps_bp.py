#!/usr/bin/env python
# coding: utf-8

import os
import sys
import yaml
import subprocess
import matplotlib.pyplot as plt

# crop region and language
crop = 'al'  # al ch lu zo
lang = 'en'  # de en fr it ja nl
mode = 'co'  # co gs


def bumper_init():
    """Init figure and axes for animation bumper."""
    figw, figh = 192.0, 108.0
    fig = plt.figure(figsize=(192.0/25.4, 108.0/25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('k')
    ax.set_xlim(-96, 96)
    ax.set_ylim(-54, 54)
    return fig, ax


def bumper_main():
    """Prepare title animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # draw text
    ax.text(0, 16, info['Title'], color='1.0', fontsize=18,
            ha='center', linespacing=1.5)
    ax.text(0, 4, info['Author'], ha='center')
    ax.text(-80, -40, info['Credit'], linespacing=1.5)

    # save
    fig.savefig('{}_4k_{}_{}.png'.format(prefix, crop, lang))
    plt.close(fig)


def bumper_bysa():
    """Prepare CC-BY-SA animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # prepare cc icon bitmaps
    for icon in ['cc', 'by', 'sa']:
        pngpath = 'icons/{}.png'.format(icon)
        svgpath = 'icons/{}.svg'.format(icon)
        cmdline = 'inkscape {} -w 640 -h 640 --export-png={}'
        if not os.path.isfile(pngpath):
            subprocess.call(cmdline.format(svgpath, pngpath).split(' '))

    # add cc icons
    ax.imshow(plt.imread('icons/cc.png'), extent=[-56, -24, 28, -4])
    ax.imshow(plt.imread('icons/by.png'), extent=[-16, +16, 28, -4])
    ax.imshow(plt.imread('icons/sa.png'), extent=[+24, +56, 28, -4])

    # draw text
    ax.text(0, -20, info['License text'], ha='center')
    ax.text(0, -32, info['License link'], ha='center', fontweight='bold')

    # save
    fig.savefig('{}_bysa_{}.png'.format(prefix, lang))
    plt.close(fig)


def bumper_disc():
    """Prepare disclaimer animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # draw text
    ax.text(0, 0, info['Disclaimer'], ha='center', va='center', linespacing=3.0)

    # save
    fig.savefig('{}_disc_{}.png'.format(prefix, lang))
    plt.close(fig)


def bumper_refs():
    """Prepare references animation bumper."""

    # initialize figure
    fig, ax = bumper_init()

    # draw text
    col1 = ''
    col2 = ''
    col3 = ''
    for category, contents in info['References'].items():
        table = [item.partition('  ') for item in contents]
        keys, _, refs = list(zip(*[item.partition('  ') for item in contents]))
        col1 += '\n' + category +' :' + '\n'*len(contents)
        col2 += '\n' + '\n'.join(keys) + '\n'
        col3 += '\n' + '\n'.join(refs) + '\n'
    ax.text(-56, 0, col1, linespacing=1.5, va='center', ha='right')
    ax.text(-40, 0, col2, linespacing=1.5, va='center', ha='left')
    ax.text(+80, 0, col3, linespacing=1.5, va='center', ha='right')

    # save
    fig.savefig('{}_refs_{}.png'.format(prefix, lang))
    plt.close(fig)


if __name__ == '__main__':
    """Plot individual frames in parallel."""

    # set default font properties
    plt.rc('figure', dpi=508)
    plt.rc('text', color='0.75')
    plt.rc('font', size=12)

    # japanese input font
    if lang == 'ja':
        plt.rc('font', family='TakaoPGothic')

    # prefix for output files
    prefix = os.path.basename(os.path.splitext(sys.argv[0])[0])

    # import text elements
    with open('anim_alps_4k_info_{}.yaml'.format(lang)) as f:
        info = yaml.load(f)

    # assemble bumpers
    bumper_main()
    bumper_bysa()
    bumper_disc()
    bumper_refs()
