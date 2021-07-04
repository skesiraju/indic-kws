#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 08 Jun 2021
# Last modified : 08 Jun 2021

"""
Get word freq histogram
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from auto_utils import get_word_count


def main():
    """ main method """

    args = parse_arguments()

    all_wcount = {}

    all_wcount = get_word_count(os.path.join(args.data_dir, "train/text"), all_wcount)
    all_wcount = get_word_count(os.path.join(args.data_dir, "dev/text"), all_wcount)
    all_wcount = get_word_count(os.path.join(args.data_dir, "test/text"), all_wcount)

    test_wcount = {}
    test_wcount = get_word_count(os.path.join(args.data_dir, "test/text"), test_wcount)

    all_counts = []
    for w in all_wcount:
        all_counts.append(all_wcount[w])

    print('all :', len(all_wcount), len(all_counts))

    test_counts = []
    for w in test_wcount:
        test_counts.append(test_wcount[w])
    print('test:', len(test_wcount), len(test_counts))

    _, axs = plt.subplots(ncols=2, figsize=(8, 4), sharey=False)

    axs[0].hist(all_counts, bins=np.arange(1, args.max_wfreq, 1))
    axs[1].hist(test_counts, bins=np.arange(1, args.max_wfreq, 1))

    for ax in axs:
        ax.grid(linestyle='--', alpha=0.5)
        ax.set_xlabel("Frequency bin")
    axs[0].set_ylabel("Number of words per bin")
    axs[0].set_title("Entire dataset")
    axs[1].set_title("Only test set")
    plt.show()


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("data_dir", help="path to data dir with train, dev, test sub dirs")
    parser.add_argument("-max_wfreq", type=int, default=31, help='max freq bin')
    # parser.add_argument("out_file", help="out file to save words")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
