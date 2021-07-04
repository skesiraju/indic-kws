#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 08 Jun 2021
# Last modified : 08 Jun 2021

"""
Get unique words from the input transcription file
"""

import os
import sys
import argparse
import numpy as np
from auto_utils import arrange_into_freq_bins, get_wfreq


def get_word_count(fname):

    wcount = {}
    with open(fname, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            for word in parts[1:]:
                try:
                    wcount[word] += 1
                except KeyError:
                    wcount[word] = 1
    return wcount


def main():
    """ main method """

    args = parse_arguments()

    wcount = get_word_count(args.trans_file)
    print("uniq words:", len(wcount))

    with open(args.out_file, 'w', encoding='utf-8') as fpw:
        i = 1
        for w in wcount:
            fpw.write(str(i) + " " + w + "\n")
            i += 1
    print(args.out_file, 'saved.')

    counts = get_wfreq(wcount)
    arrange_into_freq_bins(counts, 25)

    if args.wc:
        np.savetxt(args.wc, counts, fmt="%d")


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("trans_file", help="path to transcription file")
    parser.add_argument("out_file", help="out file to save words")
    parser.add_argument("-wc", help="save word counts to this file")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
