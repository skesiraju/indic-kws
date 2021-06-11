#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author: Santosh
# date  : Apr 05 2021

import argparse
from auto_utils import load_keywords


def get_word_freq_per_utt(trans_f):
    """ Get word frequency per utterance in nested dict format """

    # nested dict {key_word_1: {utt_id_1: count, utt_id_2: count, ...},
    #              key_word_2: {utt_id_1: count, utt_id_2: count, ...},
    #              ...
    #             }
    w_freq = {}
    with open(trans_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()
            utt_id = tokens[0]
            for tok in tokens[1:]:
                utt_freq = {}
                if tok in w_freq:
                    utt_freq = w_freq[tok]

                try:
                    utt_freq[utt_id] += 1
                except KeyError:
                    utt_freq[utt_id] = 1

                w_freq[tok] = utt_freq

    return w_freq


def get_word_freq_per_utt_from_rttm(rttm_f):
    """ Get word frequency per utterance from RTTM file """

    # nested dict {key_word_1: {utt_id_1: count, utt_id_2: count, ...},
    #              key_word_2: {utt_id_1: count, utt_id_2: count, ...},
    #              ...
    #             }
    w_rttm_freq = {}
    with open(rttm_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            if parts[0] == "LEXEME":
                # because the uttids have uttud_{lang} format in the multilingual
                utt_id = parts[1] #.rsplit("_", 1)[0]
                w = parts[-4]
                utt_freq = {}
                if w in w_rttm_freq:
                    utt_freq = w_rttm_freq[w]
                try:
                    utt_freq[utt_id] += 1
                except KeyError:
                    utt_freq[utt_id] = 1

                w_rttm_freq[w] = utt_freq

    return w_rttm_freq


def main():
    """ main method """

    args = parse_arguments()

    w_freq = get_word_freq_per_utt(args.trans_file)
    w_rttm_freq = get_word_freq_per_utt_from_rttm(args.rttm_file)

    print(
        "Found {:d} out of {:d} words in {:s}.".format(
            len(w_rttm_freq), len(w_freq), args.rttm_file
        )
    )

    # -- Compare word freqs from transcriptions and RTTM

    problems = []
    w_found = set()

    for w in w_freq:
        flag = True
        try:
            for utt_id in w_freq[w]:
                try:
                    if w_freq[w][utt_id] == w_rttm_freq[w][utt_id]:
                        continue
                    else:
                        problems.append(w + "\t" + utt_id + "missing.")
                        flag = False
                except KeyError:
                    problems.append(w + "\t" + utt_id + "missing.")
                    flag = False
        except KeyError:
            problems.append(w + " totally missing.")
            flag = False

        if flag:
            w_found.add(w)

    print(len(problems), 'issues in RTTM.')
    print(len(w_found), 'words are OK.')

    with open(args.out_problem_file, "w", encoding="utf-8") as fpw:
        fpw.write("\n".join(problems) + "\n")

    print(args.out_problem_file, "saved.")


    with open(args.out_file, "w", encoding="utf-8") as fpw:
        w_sorted = sorted(list(w_found))
        for i, w in enumerate(w_sorted):
            if args.num:
                fpw.write(str(i+1) + " " + w + "\n")
            else:
                fpw.write(w + "\n")

    print(args.out_file, "saved with", len(w_found), "words -->", end=" ")

    if args.num:
        print("Two column entries: <num> <word>")
    else:
        print("Single column entries: <word>. Use --num option to save it in <num> <word> format.")


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("trans_file", help="path to train/test transcription text file")
    parser.add_argument("rttm_file", help="path to rttm_file")
    parser.add_argument("out_file", help="out file to save the words that are all OK.")
    parser.add_argument("out_problem_file", help="out file to save the problems from RTTM.")
    parser.add_argument("--num", action="store_true", help="save in <num> <word> format.")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
