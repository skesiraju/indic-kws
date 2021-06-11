#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import numpy as np
from Levenshtein import distance  # pylint: disable=no-name-in-module


def load_keywords(kw_file, lex):
    """ load keywords """

    kwords = []
    orig_kwords = []

    with open(kw_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()

            # check if its in two column format or single column
            if len(parts) == 2:
                kwords.append(lex[parts[-1]])
                orig_kwords.append(parts[-1])
            else:
                kwords.append(lex[parts])
                orig_kwords.append(parts[0])

    return kwords, orig_kwords


def load_lexicon(lex_file, phone_rep):
    """ Load lexicon into dict """

    lex = {}  # key is utf-8 word, value is list of phones
    with open(lex_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            lex[parts[0]] = "".join([phone_rep[p] for p in parts[1:]])
    return lex


def load_text_and_convert(text_file, lex):
    """ convert unicode text to single character graphemic representation """

    utt_ids = []
    text = []
    with open(text_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            line_str = ""
            words = line.strip().split()
            utt_ids.append(words[0])
            for w in words[1:]:
                try:
                    line_str += lex[w] + " "
                except KeyError:
                    print("Error:", w, "is not present in the given lexicon.")
                    sys.exit()
            text.append(line_str.strip())

    return utt_ids, text


def get_min_distance(kword, text):
    """ Get min Levenshtein distance of the kword in the text """

    dists = []
    words = text.split()
    for w in words:
        if w == kword:
            pass
        else:
            dw = distance(w, kword)
            dists.append(dw)
    if not dists:
        return 0
    else:
        return np.min(dists)


def main():
    """ main method """

    args = parse_arguments()

    os.makedirs(args.out_dir, exist_ok=True)

    out_dir = os.path.realpath(args.out_dir)

    print("Out dir:", out_dir)

    for dist in range(args.min_dist, args.max_dist + 1, 1):
        fname = f"{out_dir}/avg_conf_{dist}.txt"
        with open(fname, "w") as fpw:
            fpw.write("")
            # if args.line_nums:
            # fpw.write("key_word_number, key_word\n")
            # else:
            #    fpw.write("key_word_number, key_word\n")

    # single character graphemic mapping
    phone_rep = {}
    with open(args.repr_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            phone_rep[parts[0]] = parts[1]

    lex = load_lexicon(args.lex_file, phone_rep)

    print("Lexicon size:", len(lex))

    kwords, orig_kwords = load_keywords(args.kw_file, lex)

    # convert unicode text to single character graphemic representation
    _, text = load_text_and_convert(args.text_file, lex)

    for kno, kword in enumerate(kwords):
        all_dists = []
        for _, line in enumerate(text):

            dist = get_min_distance(kword, line)
            if dist > 0:
                all_dists.append(dist)

        avg_dist = int(np.mean(all_dists))
        if args.min_dist <= avg_dist <= args.max_dist:
            with open(f"{out_dir}/avg_conf_{avg_dist}.txt", "a") as fpa:
                fpa.write(str(kno + 1) + " " + orig_kwords[kno] + "\n")


def parse_arguments():
    """ parse command line args """

    parser = argparse.ArgumentParser()
    parser.add_argument("kw_file", help="path to keywords text file")
    parser.add_argument("lex_file", help="path to lexicon text file")
    parser.add_argument("repr_file", help="path to phone_repr.txt file")
    parser.add_argument("text_file", help="path to train/test text file")
    parser.add_argument("out_dir", help="output directory to save files")
    parser.add_argument("-min_dist", type=int, default=2, help="min distance")
    parser.add_argument("-max_dist", type=int, default=8, help="max distance")

    # parser.add_argument("--line_nums", action="store_true",
    #                     help="save utterance line numbers instead of IDs")

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    main()
