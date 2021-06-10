#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Santosh
# e-mail : kcraj2[AT]gmail[DOT]com
# Date created : 27 Apr 2021
# Last modified : 27 Apr 2021

"""
"""

import os
import sys
import argparse
import numpy as np


def load_into_dict(fname, delim=" ", val_is_float=False):
    """ load uttID val into dict """

    utt_dict = {}
    i = 0
    with open(fname, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            parts = line.strip().split(delim, 1)
            utt_id = parts[0]
            if val_is_float:
                val = float(parts[1].strip())
            else:
                val = parts[1].strip()

            utt_dict[utt_id] = val
            # print(utt_id, val)

            # i += 1
            # if i >= 10:
            #    break

    return utt_dict


def sort_utts_on_dur(utt2dur):
    """ sort utts based on duration """

    utts = []
    durs = []
    for utt_id, dur in utt2dur.items():
        utts.append(utt_id)
        durs.append(dur)

    sort_ixs = np.argsort(np.asarray(durs))
    return np.asarray(utts, dtype=str)[sort_ixs].tolist(), np.asarray(durs, dtype=str)[sort_ixs].tolist(),

def main():
    """ main method """

    args = parse_arguments()

    # format: sorted according to utt_dur
    # utt_ID path_to_wav_file utt_dur utt_text

    lex_file = os.path.join(args.data_dir, "local/dict/lexicon.txt")
    word2phn = load_into_dict(lex_file, delim="\t")
    print("lexicon:", len(word2phn))

    for set_name in ["train", "dev", "test"]:

        utt2dur_f = os.path.join(args.data_dir, f"{set_name}/utt2dur")
        text_f = os.path.join(args.data_dir, f"{set_name}/text")
        wav_scp = os.path.join(args.data_dir, f"{set_name}/wav.scp")

        utt2dur = load_into_dict(utt2dur_f, val_is_float=True)
        utt2text = load_into_dict(text_f)
        utt2wav = load_into_dict(wav_scp)

        print(set_name, len(utt2dur), len(utt2text), len(utt2wav))

        sorted_utts, sorted_durs = sort_utts_on_dur(utt2dur)

        out_f = os.path.join(args.data_dir, f"{set_name}.lst")

        with open(out_f, 'w', encoding='utf-8') as fpw:
            for utt_id in sorted_utts:
                fpw.write(
                    utt_id + " " + utt2wav[utt_id] + " " + \
                    str(utt2dur[utt_id]) + " " + utt2text[utt_id] + "\n"
                )
        print(out_f, "saved.")

    with open(os.path.join(args.data_dir, "lex_forwav2let.txt"), "w", encoding="utf-8") as fpw:
        for word, phn in word2phn.items():
            fpw.write(word + "\t" + phn + " |\n")

    tokens = set()
    for word, phns in word2phn.items():
        phones = phns.split()
        for p in phones:
            tokens.add(p)

    print('phones:', len(tokens))
    tokens = list(tokens)
    with open(os.path.join(args.data_dir, "tokens.txt"), "w", encoding="utf-8") as fpw:
        for i, t in enumerate(tokens):
            fpw.write(t + "\n")
        fpw.write("|")


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("data_dir")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
