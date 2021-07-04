#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 29 Jun 2021
# Last modified : 29 Jun 2021

"""
select keywords in the given wfreq and wlen bin
"""

import os
import sys
import argparse
import numpy as np
from auto_utils import (
    write_kw_to_file,
    get_kw_count,
    get_wfreq_bin_dict,
    arrange_into_freq_bins,
    get_wfreq,
    load_keywords,
    get_wlen,
    get_wlen_dict,
    load_lexicon,
    get_wset,
    CAP,
    CUP,
)


def main():
    """ main method """

    args = parse_arguments()

    print("* In text file:", args.text_file)
    data_dir = "data/"

    lex = load_lexicon(os.path.join(data_dir, "local/dict/lexicon.txt"))
    print("* Lexicon:", len(lex))

    keywords = load_keywords(args.kw_file)
    print("# keywords:", len(keywords))

    # train_w_count = get_kw_count(os.path.join(data_dir, "train/text"), keywords)
    # dev_w_count = get_kw_count(os.path.join(data_dir, "dev/text"), keywords)
    test_w_count = get_kw_count(args.text_file, keywords)

    # print("train w count:", len(train_w_count))
    # print("dev   w count:", len(dev_w_count))
    print("test w count dict :", len(test_w_count))

    test_w_len = get_wlen_dict(test_w_count, lex)
    print("test w len  dict  :", len(test_w_len))

    test_wf_bin_dict = get_wfreq_bin_dict(test_w_count)
    print("test wf bin dict  :", len(test_wf_bin_dict))

    test_wlen_bin_dict = get_wfreq_bin_dict(test_w_len)
    print("test wlen bin dict:", len(test_wlen_bin_dict))

    test_wlens = get_wlen(test_w_count, lex)
    arrange_into_freq_bins(test_wlens, 25, name="wlen")

    wlen_words = set(test_wlen_bin_dict[args.wlen])
    wfreq_words = set(test_wf_bin_dict[args.wfreq])

    # print(len(wlen_words), len(wfreq_words))

    common_words = wlen_words & wfreq_words
    print("common words:", len(common_words))

    if len(common_words) > 1:
        i = 1
        with open(args.out_file, "w", encoding="utf-8") as fpw:
            for w in common_words:
                fpw.write(str(i) + " " + w + "\n")
                i += 1
        print(args.out_file, "saved.")


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("kw_file", help="path to keywords file")
    parser.add_argument("wfreq", type=int, help="wfreq bin")
    parser.add_argument("wlen", type=int, help="wlen bin")
    parser.add_argument("out_file", help="path to out file")
    parser.add_argument("-text_file", default="data/test/text", help="path to text file")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
