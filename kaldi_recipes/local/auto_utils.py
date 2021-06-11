#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Santosh
# e-mail : kcraj2[AT]gmail[DOT]com
# Date created : 02 Apr 2021
# Last modified : 02 Apr 2021

"""
Several helper functions for automatic keyword selection
"""

import os
import sys
import numpy as np


CAP = u"\u2229"
CUP = u"\u222A"

get_wset = lambda w_count: set([k for k in w_count])

get_wlen = lambda w_count, lex: [len(lex[k]) for k in w_count]

get_wfreq = lambda w_count: [v for k, v in w_count.items()]


def load_lexicon(lex_file):

    print("Loading lexicon from file:", lex_file)
    print("  Return dict will have: {word_1: [ph_1, ph_2, ph_3 ...], ...}")
    lex = {}
    with open(lex_file, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            line = line.strip()
            parts = line.split("\t")
            # print(line, parts)
            lex[parts[0].strip()] = parts[1].split()

    return lex


def load_keywords(keywords_file):

    keywords = set()
    with open(keywords_file, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            line = line.strip()
            parts = line.split()
            if len(parts) == 1:
                keywords.add(parts[0])
            elif len(parts) == 2:
                keywords.add(parts[-1])
            else:
                print("keywords file should have either 1 or 2 columns. Found:",
                      line)
                sys.exit()
    return keywords



def get_kw_count(trans_file, keywords):
    kw_count = {}
    with open(trans_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()[1:]
            for tok in tokens:
                if tok in keywords:
                    try:
                        kw_count[tok] += 1
                    except KeyError:
                        kw_count[tok] = 1

    print("{:4d}".format(len(kw_count)), "keywords found in", trans_file)

    return kw_count


def get_kw_and_word_count(trans_file, keywords):

    word_count = {}
    kw_count = {}
    with open(trans_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()[1:]
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


def get_word_count(trans_file):

    word_count = {}
    # kw_count = {}
    with open(trans_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()[1:]
            for tok in tokens:
                try:
                    word_count[tok] += 1
                except KeyError:
                    word_count[tok] = 1

    print("  Total number of unique words:", len(word_count))

    return word_count


def get_wfreq_bin_dict(kw_count):

    bin_dict = {}
    for kw, occ in kw_count.items():
        try:
            bin_dict[occ].append(kw)
        except KeyError:
            bin_dict[occ] = [kw]
    return bin_dict


def write_kw_to_file(keywords, fname):

    with open(fname, 'w', encoding='utf-8') as fpw:
         for i, k in enumerate(keywords):
             fpw.write(str(i+1) + " " + k + "\n")

    print(len(keywords), "keywords saved to", fname)


def arrange_into_freq_bins(counts, max_bin):

    bin_sizes, bins = np.histogram(counts, bins=np.arange(1, max_bin))
    print("bins     :", bins.tolist())
    print('bin sizes:', bin_sizes.tolist(), 'sum:', sum(bin_sizes))
