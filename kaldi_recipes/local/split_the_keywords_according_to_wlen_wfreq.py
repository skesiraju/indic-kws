#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh
# e-mail : kcraj2[AT]gmail[DOT]com
# Date created : 02 Apr 2021
# Last modified : 02 Apr 2021

"""
"""

import os
import sys
import argparse
from auto_utils import (load_lexicon, load_keywords, write_kw_to_file, get_word_count)


def write_kw_bins_to_separate_files(bin_dict, par_name, out_dir):

    par_dir = os.path.join(out_dir, par_name)
    os.makedirs(par_dir, exist_ok=True)

    for par in bin_dict:
        if len(bin_dict[par]) <= 2 and par_name == "wlen":
            continue
        if par <= 2 and par_name == "wlen":
            continue
        out_f = os.path.join(par_dir, f"{par_name}_{par}.txt")
        write_kw_to_file(bin_dict[par], out_f)

    print("Saved in", par_dir)


def main():
    """ main method """

    args = parse_arguments()
    os.makedirs(args.out_dir, exist_ok=True)

    if os.path.exists(args.lexicon_file):
        lex = load_lexicon(args.lexicon_file)
        print("Lex:", len(lex))
    else:
        print("Cannot find", args.lexicon_file)
        print("use -lexicon_file arg")
        sys.exit()

    w_count = get_word_count(args.trans_file)

    kws = load_keywords(args.keywords_file)
    print("Kws:", len(kws))

    wlen_bins = {}
    wfreq_bins = {}

    for kw in kws:
        wfreq_i = w_count[kw]
        wlen_i = len(lex[kw])

        try:
            wlen_bins[wlen_i].append(kw)
        except KeyError:
            wlen_bins[wlen_i] = [kw]

        try:
            wfreq_bins[wfreq_i].append(kw)
        except KeyError:
            wfreq_bins[wfreq_i] = [kw]

    print('wfreq bins:', len(wfreq_bins), 'wlen bins:', len(wlen_bins))


    write_kw_bins_to_separate_files(wfreq_bins, "wfreq", args.out_dir)
    write_kw_bins_to_separate_files(wlen_bins, "wlen", args.out_dir)




def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keywords_file")
    parser.add_argument("out_dir")
    parser.add_argument("-trans_file", default="data/test/text")
    parser.add_argument("-lexicon_file", default="data/local/dict/lexicon.txt")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
