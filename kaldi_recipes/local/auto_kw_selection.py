#!/usr/bin/env python3

import os
import sys
import argparse
import numpy as np
# import matplotlib.pyplot as plt


# PATHS = ["data/train/text", "data/dev/text", "data/test/text"]



def get_kw_and_word_count(trans_file, keywords):

    word_count = {}
    kw_count = {}
    with open(trans_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()
            for tok in tokens:
                if tok in keywords:
                    try:
                        kw_count[tok] += 1
                    except KeyError:
                        kw_count[tok] = 1
                try:
                    word_count[tok] += 1
                except KeyError:
                    word_count[tok] = 1

    print("Found", len(kw_count), "keywords in", trans_file,
          "({:3.1f}%)".format(len(kw_count) * 100 / len(keywords)))
    print("  Total number of unique words:", len(word_count))

    return kw_count, word_count



def arrange_into_freq_bins(counts, max_bin):

    bin_sizes, bins = np.histogram(counts, bins=np.arange(1, max_bin))
    print('bin sizes:', bin_sizes, 'sum:', sum(bin_sizes))
    # print('bins     :', bins)


kw_len = lambda kw_count: [len(k) for k in kw_count]

kw_freq = lambda kw_count: [v for k, v in kw_count.items()]

def main():
    """ main method """

    keywords = set()
    with open(args.keywords_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            if len(line.strip().split()) == 2:
                keywords.add(line.strip().split()[-1])
            else:
                keywords.add(line.strip())

    print("Loaded", len(keywords), "keywords from", args.keywords_file)

    data_dir = args.data_dir

    train_kw_count, train_w_count = get_kw_and_word_count(os.path.join(data_dir, "train/text"), keywords)
    dev_kw_count, dev_w_count = get_kw_and_word_count(os.path.join(data_dir, "dev/text"), keywords)
    test_kw_count, test_w_count = get_kw_and_word_count(os.path.join(data_dir, "test/text"), keywords)

    train_count = kw_freq(train_kw_count)
    dev_count = kw_freq(dev_kw_count)
    test_count = kw_freq(test_kw_count)

    print("== word occurrence ==")
    arrange_into_freq_bins(train_count, args.max_bin)
    arrange_into_freq_bins(dev_count, args.max_bin)
    arrange_into_freq_bins(test_count, args.max_bin)

    print("== word length ==")

    train_kw_lens = kw_len(train_kw_count)
    arrange_into_freq_bins(train_kw_lens, args.max_bin)

    dev_kw_lens = kw_len(dev_kw_count)
    arrange_into_freq_bins(dev_kw_lens, args.max_bin)

    test_kw_lens = kw_len(test_kw_count)
    arrange_into_freq_bins(test_kw_lens, args.max_bin)



    sys.exit()

    not_in_train = {}
    not_in_train_count = []
    for kw in keywords:
        if kw not in train_kw_count:
            not_in_train[kw] = test_kw_count[kw]
            not_in_train_count.append(test_kw_count[kw])

    print("Not in train:", len(not_in_train))

    print("Histogram")
    print(np.histogram(test_count, bins=np.unique(test_count)))

    print("-- Not in train --")
    print(not_in_train_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("keywords_file", help="path to keywords file")
    parser.add_argument("data_dir", help="path to data dir")
    parser.add_argument('-max_bin', type=int, default=10)
    args = parser.parse_args()

    main()
