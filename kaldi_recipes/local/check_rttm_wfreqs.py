#!/usr/bin/env python3
# coding: utf-8

# author: Santosh
# date  : Mar 03 2021

import argparse


def load_keywords(keyword_f):

    kws = set()
    with open(keyword_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            kws.add(parts[-1].strip())

    return kws


def get_kw_freq(kws, trans_f):

    kw_freq = {}
    with open(trans_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()[1:]
            for tok in tokens:
                if tok in kws:
                    try:
                        kw_freq[tok] += 1
                    except KeyError:
                        kw_freq[tok] = 1

    return kw_freq


def get_kw_freq_from_rttm(kws, rttm_f):

    kw_rttm_freq = {}
    with open(rttm_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            if parts[0] == "LEXEME":
                kw = parts[-4]
                if kw in kws:
                    try:
                        kw_rttm_freq[kw] += 1
                    except KeyError:
                        kw_rttm_freq[kw] = 1

    return kw_rttm_freq


def main():

    args = parse_arguments()

    kws = load_keywords(args.keyword_file)

    print("Loaded {:d} kyewords from {:s}".format(len(kws), args.keyword_file))

    kw_freq = get_kw_freq(kws, args.trans_file)

    if len(kws) != len(kw_freq):
        print("PROBLEM", end=" ")
    else:
        print("OKAY   ", end="")

    print(
        "Found {:d} out of {:d} keywords in {:s}.".format(
            len(kw_freq), len(kws), args.trans_file
        )
    )

    if len(kws) != len(kw_freq):
        print("PROBLEM", end=" ")
    else:
        print("OKAY   ", end="")

    kw_rttm_freq = get_kw_freq_from_rttm(kws, args.rttm_file)

    print(
        "Found {:d} out of {:d} keywords in {:s}.".format(
            len(kw_rttm_freq), len(kws), args.rttm_file
        )
    )

    # -- Compare word freqs from transcriptions and RTTM

    for kw in kws:
        try:
            if kw_freq[kw] == kw_rttm_freq[kw]:
                continue
            else:
                print(
                    "PROBLEM: {:20s} was found {:2d} times transcription but only {:2d} times in RTTM file.".format(
                        kw.strip(), kw_freq[kw], kw_rttm_freq[kw]
                    )
                )
        except KeyError:
            print("PROBLEM: {:20s} was not found in RTTM file.".format(kw))


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("keyword_file", help="path to keywords.txt file")
    parser.add_argument("trans_file", help="path to train/test transcription text file")
    parser.add_argument("rttm_file", help="path to rttm_file")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()

