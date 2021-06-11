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

    # nested dict {key_word_1: {utt_id_1: count, utt_id_2: count, ...},
    #              key_word_2: {utt_id_1: count, utt_id_2: count, ...},
    #              ...
    #             }
    kw_freq = {}
    with open(trans_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()
            utt_id = tokens[0]
            for tok in tokens[1:]:
                if tok in kws:
                    utt_freq = {}
                    if tok in kw_freq:
                        utt_freq = kw_freq[tok]

                    try:
                        utt_freq[utt_id] += 1
                    except KeyError:
                        utt_freq[utt_id] = 1

                    kw_freq[tok] = utt_freq

    return kw_freq


def get_kw_freq_from_rttm(kws, rttm_f):

    # nested dict {key_word_1: {utt_id_1: count, utt_id_2: count, ...},
    #              key_word_2: {utt_id_1: count, utt_id_2: count, ...},
    #              ...
    #             }
    kw_rttm_freq = {}
    with open(rttm_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            if parts[0] == "LEXEME":
                # because the uttids have uttud_{lang} format in the multilingual
                utt_id = parts[1] #.rsplit("_", 1)[0]
                kw = parts[-4]
                if kw in kws:
                    utt_freq = {}
                    if kw in kw_rttm_freq:
                        utt_freq = kw_rttm_freq[kw]
                    try:
                        utt_freq[utt_id] += 1
                    except KeyError:
                        utt_freq[utt_id] = 1

                    kw_rttm_freq[kw] = utt_freq

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

    problems = []

    for kw in kws:
        try:
            for utt_id in kw_freq[kw]:
                try:
                    if kw_freq[kw][utt_id] == kw_rttm_freq[kw][utt_id]:
                        continue
                    else:
                        print(
                            "PROBLEM: {:20s} in utt_id {:s} was found {:2d} times in transcription but only {:2d} times in RTTM file.".format(
                                kw.strip(), utt_id, kw_freq[kw], kw_rttm_freq[kw]
                            )
                        )
                        problems.append(utt_id + "\t" + kw)
                except KeyError:
                    print("{:s} from utt_id missing in RTTM {:s}".format(kw, utt_id))
                    problems.append(utt_id + "\t" + kw)
        except KeyError:
            print("PROBLEM: {:20s} was not found in RTTM file.".format(kw))

    print(len(problems), 'issues.')
    with open(args.out_file, "w", encoding="utf-8") as fpw:
        fpw.write("\n".join(problems) + "\n")


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("keyword_file", help="path to keywords.txt file")
    parser.add_argument("trans_file", help="path to train/test transcription text file")
    parser.add_argument("rttm_file", help="path to rttm_file")
    parser.add_argument("out_file", help="out file to save the missing utt_ids and kws")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
