#!/usr/bin/env python3

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from auto_utils import (load_keywords, get_wset, get_wlen, get_wfreq,
                        CAP, CUP, arrange_into_freq_bins, write_kw_to_file,
                        get_wfreq_bin_dict, arrange_into_freq_bins)



def main():

    keywords = load_keywords(args.keyword_file)

    print("# keywords", len(keywords))

    train_kw_count = get_kw_count(args.train_text, keywords)
    dev_kw_count = get_kw_count(args.dev_text, keywords)
    test_kw_count = get_kw_count(args.test_text, keywords)

    train_wset = get_wset(train_kw_count)
    dev_wset = get_wset(dev_kw_count)
    test_wset = get_wset(test_kw_count)

    train_count = get_wfreq(train_kw_count)
    dev_count = get_wfreq(dev_kw_count)
    test_count = get_wfreq(test_kw_count)

    tdt_set = (test_wset & train_wset) & dev_wset
    print(f"C = (train {CAP} dev {CAP} test):", len(tdt_set))

    tt_set = (train_wset & test_wset) - tdt_set
    print(f"T = (train {CAP} test) - C  :", len(tt_set))

    dt_set = (dev_wset & test_wset) - tdt_set
    print(f"D = (dev   {CAP} test) - C  :", len(dt_set))

    t_set = test_wset - (tdt_set | tt_set | dt_set)
    print(f"test - (C {CUP} T {CUP} D)      :", len(t_set))

    arrange_into_freq_bins(train_count, 15)
    arrange_into_freq_bins(dev_count, 15)
    arrange_into_freq_bins(test_count, 15)

    print('test_count:', sum(test_count))
    wf_bin_dict = get_wfreq_bin_dict(test_kw_count)
    print('wf bin dict:', len(wf_bin_dict))
    bin_sizes, bins = np.histogram(test_count, bins=np.unique(test_count))
    print(bins.tolist())
    filtered_kw = []
    max_bsize = bin_sizes[0]
    print(bins[0], max_bsize)
    prev_lim = 0
    for bin_ix in bins:
        if bin_ix not in wf_bin_dict:
            continue
        if bin_ix == 1:
            filtered_kw += wf_bin_dict[bin_ix]
            continue
        else:
            lim = int(max_bsize - (max_bsize * (bin_ix/9.)))
            if lim <= 0:
                lim = min(int(prev_lim * 0.9), int(len(wf_bin_dict[bin_ix])*0.9))
            print(bin_ix, lim)
            filtered_kw += wf_bin_dict[bin_ix][:lim]
            prev_lim = lim

    write_kw_to_file(filtered_kw, args.out_file)
    print(args.out_file, 'saved.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword_file")
    parser.add_argument("out_file")
    parser.add_argument("-train_text", default="data/train/text")
    parser.add_argument("-dev_text", default="data/dev/text")
    parser.add_argument("-test_text", default="data/test/text")

    args = parser.parse_args()

    main()
