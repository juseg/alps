#!/usr/bin/env python
# Copyright (c) 2020-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Alps erosion landscape photographs."""

import os.path
import urllib.request
import matplotlib.pyplot as plt
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(177, 41), ncols=3, sharex=True, sharey=True, gridspec_kw=dict(
            left=1.5, right=1.5, bottom=1.5, top=1.5, hspace=1.5, wspace=1.5))

    # flickr photo identifiers
    photos = [  # use _b for 1024, _c for 800 px
        '50743485202_405601c2d8_b.jpg',
        '50743484067_800c6cfba8_b.jpg',
        '50742646803_2bd4961b6a_b.jpg']

    # loop on axes
    for i, ax in enumerate(grid):

        util.fig.add_subfig_label('(%s)' % list('abc')[i], ax=ax)
        ax.set_xticks([])
        ax.set_yticks([])

        # download photo if missing
        if not os.path.isfile(photos[i]):
            urllib.request.urlretrieve(
                'https://live.staticflickr.com/65535/'+photos[i], photos[i])

        # plot photo
        ax.imshow(plt.imread(photos[i]))

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
