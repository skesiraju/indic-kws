#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Santosh
# e-mail : kcraj2[AT]gmail[DOT]com
# Date created : 02 Apr 2021
# Last modified : 02 Apr 2021

"""
Select keywords from alignment that satisfy the given conditions
"""

import os
import sys
import argparse
import numpy as np
from auto_utils import (
    write_kw_to_file, get_kw_count, get_wfreq_bin_dict, arrange_into_freq_bins,
    get_wfreq, load_keywords, get_wlen, load_lexicon, get_wset, CAP, CUP
)


def get_wixs(words, subset):

    ixs = []
    sub_words = []
    for i, w in enumerate(words):
        if w in subset:
            ixs.append(i)
            sub_words.append(w)
    return ixs, sub_words


def select_words(words, det, ixs, cur_target_num, args):

    hit_prob = det[ixs, 0] / det[ixs, :2].sum(axis=1)
    print(' prob of hit vector:', hit_prob.shape)

    num_miss = int(args.mr * cur_target_num)
    num_hits = cur_target_num - num_miss

    miss_ixs = np.where(hit_prob <= args.thresh)[0]
    hit_ixs = np.where(hit_prob > args.thresh)[0]

    print(' miss ixs:', len(miss_ixs), 'hit ixs:', len(hit_ixs))

    w_ixs = miss_ixs[:num_miss].tolist() + hit_ixs[:num_hits].tolist()

    print(" Desired : num_miss=", num_miss, "num_hits=", num_hits)

    o_miss = min(num_miss, len(miss_ixs))
    o_hits = min(num_hits, len(hit_ixs))
    print(" Observed: num_miss=", o_miss, "num_hits=", o_hits)

    sel_words = []
    for i in w_ixs:
        sel_words.append(words[i])

    return sel_words, num_miss - o_miss, num_hits - o_hits


def main():
    """ main method """

    args = parse_arguments()

    data_dir = "data/"

    lex = load_lexicon(os.path.join(data_dir, "local/dict/lexicon.txt"))
    print("* Lexicon:", len(lex))

    keywords = load_keywords(args.kw_file)

    train_w_count = get_kw_count(os.path.join(data_dir, "train/text"), keywords)
    dev_w_count = get_kw_count(os.path.join(data_dir, "dev/text"), keywords)
    test_w_count = get_kw_count(os.path.join(data_dir, "test/text"), keywords)

    test_wf_bin_dict = get_wfreq_bin_dict(test_w_count)

    train_wset = get_wset(train_w_count)
    dev_wset = get_wset(dev_w_count)
    test_wset = get_wset(test_w_count)

    train_count = get_wfreq(train_w_count)
    dev_count = get_wfreq(dev_w_count)
    test_count = get_wfreq(test_w_count)

    arrange_into_freq_bins(test_count, args.max_bin)

    # print("== word length ==")
    # train_w_lens = get_wlen(train_w_count, lex)
    # arrange_into_freq_bins(train_w_lens, args.max_bin)

    # dev_w_lens = get_wlen(dev_w_count, lex)
    # arrange_into_freq_bins(dev_w_lens, args.max_bin)

    # test_w_lens = get_wlen(test_w_count, lex)
    # arrange_into_freq_bins(test_w_lens, args.max_bin)


    tdt_set = (test_wset & train_wset) & dev_wset
    print(f"C = (train {CAP} dev {CAP} test):", len(tdt_set))

    tt_set = (train_wset & test_wset) - tdt_set
    print(f"T = (train {CAP} test) - C  :", len(tt_set))

    dt_set = (dev_wset & test_wset) - tdt_set
    print(f"D = (dev   {CAP} test) - C  :", len(dt_set))

    t_set = test_wset - (tdt_set | tt_set | dt_set)
    print(f"X = test - (C {CUP} T {CUP} D)  :", len(t_set))

    print("-- Loading info from alignment.csv --")

    # contains info from alignment.csv
    word_det = {}  # {word_1: [num_hits, num_miss, num_fa], ..}

    legend = ["CORR", "MISS", "FA"]

    with open(args.alignments_file, 'r', encoding='utf-8') as fpr:
        header = fpr.readline().strip().split(",")
        for line in fpr:
            parts = line.strip().split(",")
            word = parts[4].strip()
            if word.strip():
                val = [0, 0, 0]
                ix = -1
                if parts[-1] == "CORR":
                    val[0] = 1
                    ix = 0
                if parts[-1] == "MISS":
                    val[1] = 1
                    ix = 1
                if parts[-1] == "FA":
                    val[2] = 1
                    ix = 2

                if ix != -1:
                    try:
                        word_det[word][ix] += 1
                    except KeyError:
                        word_det[word] = val

    print('word det:', len(word_det), word_det.keys())

    det = []
    words = []
    to_delete = []
    for word, val in word_det.items():
        try:
            if test_w_count[word] == args.wfreq or args.wfreq == 0:
                words.append(word)
                det.append(val)
        except KeyError:
            to_delete.append(word)

    if to_delete:
        for w in to_delete:
            print("deleting", w)
            del word_det[w]


    det = np.asarray(det)
    print('det:', det.shape, 'words with wfreq', args.wfreq, '. F =', len(words))

    X_and_F = t_set & set(words)
    print(f"X {CAP} F", len(X_and_F))
    F_min_X = set(words) - t_set
    print("F - X", len(F_min_X))

    a_miss = 0
    a_hits = 0
    sub_set_t = []
    if len(X_and_F) >= (args.target_num * args.test_ratio):

        print("Will select {:4.1f}% from X {:s} F and rest from F - X".format(
            (args.test_ratio*100.), CAP))

        ixs, sub_words = get_wixs(words, X_and_F)

        sub_set_t, a_miss, a_hits = select_words(
            sub_words, det, ixs, int(args.target_num * args.test_ratio), args
        )

        print('selected so far:', len(sub_set_t))

    else:
        print(f"Too little in X {CAP} F")

    # re-adjusting the desired number of misses and hits

    rem_num = args.target_num - len(sub_set_t)

    if rem_num > 0:
        num_miss = (args.target_num * args.mr)
        args.mr = float(num_miss  + a_miss) / float(rem_num)

    print('remaining target num:', rem_num, 'adjusted miss ratio:', args.mr)

    ixs, sub_words = get_wixs(words, F_min_X)
    sub_set_a, a_miss, a_hits = select_words(sub_words, det, ixs, rem_num, args)

    print('sub_set_a:', len(sub_set_a), 'a_miss:', a_miss, 'a_hits:', a_hits)

    sel_words = sub_set_t + sub_set_a

    write_kw_to_file(sel_words, args.out_file)


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kw_file", help="input keyword file")
    parser.add_argument("alignments_file", help="alignment file related to the above keyword file")
    parser.add_argument("out_file", help="out file to save keywords")
    parser.add_argument("wfreq", type=int, help="wfreq condition")
    parser.add_argument("target_num", type=int, help="target number of keywords")
    parser.add_argument("-mr", default=0.3, type=float, help="miss percent of target num")
    parser.add_argument("-thresh", default=0, type=float,
                        help="threshold for deciding what is considered as a miss. \
Should be less than 0.5. Should be 0 when wfreq <= 3")
    parser.add_argument("-test_ratio", default=0.3, type=float, help="number of keywords to be exclusive to test set")

    args = parser.parse_args()
    args.max_bin = 25  # max wfreq and max wlen
    return args

if __name__ == "__main__":
    main()
