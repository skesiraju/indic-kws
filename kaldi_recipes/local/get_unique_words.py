#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 08 Jun 2021
# Last modified : 08 Jun 2021

"""
Get unique words in train/test and also their intersection
"""

import os
import sys
import argparse


def get_word_count(fname):

    wcount = {}
    with open(fname, 'r', encoding='utf-8') as fpr:
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

    train_f = os.path.join(args.data_dir, "train/text")
    test_f = os.path.join(args.data_dir, "test/text")

    train_wc = get_word_count(train_f)
    test_wc = get_word_count(test_f)

    train_vocab = set([w for w in train_wc])
    test_vocab = set([w for w in test_wc])

    print("train vocab :", len(train_vocab), len(train_wc))
    print("test  vocab :", len(test_vocab), len(test_wc))

    print("train & test:", len(train_vocab & test_vocab))
    print("train - test:", len(train_vocab - test_vocab))
    print("test - train:", len(test_vocab - train_vocab))

    counts = []
    for w in test_vocab - train_vocab:
        counts.append(test_wc[w])

    import matplotlib.pyplot as plt
    import numpy as np
    plt.figure(1)
    plt.title(args.title + " test set")
    plt.hist(counts, bins=np.arange(1, max(counts)+1, 1))
    plt.grid(linestyle='--', alpha=0.5)
    plt.xlabel('Occurrence bin')
    plt.ylabel('Occurrence')
    plt.show()

    print(np.histogram(counts, bins=np.arange(1, max(counts)+1, 1)))



def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("data_dir", help="path to data dir")
    parser.add_argument("-title", default="")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
