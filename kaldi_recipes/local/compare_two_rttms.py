#!/usr/bin/env python3
# coding: utf-8

# author: Santosh
# date  : Mar 03 2021

import sys
import argparse


def load_keywords(keyword_f):

    kws = set()
    with open(keyword_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            kws.add(parts[-1].strip())

    return kws


def get_unique_words_from_rttm(rttm_f, kws):

    kw_rttm_freq = {}
    kws_ts = {}  # keyword time stamps
    with open(rttm_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split()
            if parts[0] == "LEXEME":
                kw = parts[-4]
                try:
                    kw_rttm_freq[kw] += 1
                except KeyError:
                    kw_rttm_freq[kw] = 1

                if kw in kws:
                    utt_id = parts[1]
                    stime = float(parts[3])
                    etime = float(parts[4])
                    sub_dict = {}
                    if utt_id not in kws_ts:
                        kws_ts[utt_id] = sub_dict

                    if kw not in sub_dict:
                        sub_dict[kw] = [stime, etime]
                    else:
                        sub_dict[kw].extend([stime, etime])

    return kw_rttm_freq, kws_ts


def get_unique_words_from_transcription(trans_f):

    word_freq = {}
    with open(trans_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()[1:]
            for tok in tokens:
                try:
                    word_freq[tok] += 1
                except KeyError:
                    word_freq[tok] = 1

    return word_freq


def are_all_kws_present(kws, word_freq):
    """ Check if all the kws are found in word_freq """

    not_found = []
    for kw in kws:
        if kw not in word_freq:
            not_found.append(kw)
    return not_found


def compare_wfreqs(kws, kw_freq, kw_rttm_freq):

    flag = True

    for kw in kws:
        try:
            if kw_freq[kw] == kw_rttm_freq[kw]:
                continue
            else:
                print(
                    "  PROBLEM: {:20s} was found {:2d} times transcription but only {:2d} times in RTTM file.".format(
                        kw.strip(), kw_freq[kw], kw_rttm_freq[kw]
                    )
                )
                flag = False
        except KeyError:
            print("  PROBLEM: {:20s} was not found in RTTM file.".format(kw))
            flag = False

    return flag


def main():

    args = parse_arguments()

    kws = load_keywords(args.keywords_f)
    print("Loaded {:d} keywords from {:s}".format(len(kws), args.keywords_f))

    word_freq_trans = get_unique_words_from_transcription(args.test_trans_f)
    print(
        "Found {:d} unique words in transcription {:s}".format(
            len(word_freq_trans), args.test_trans_f
        ),
        end="\t -- ",
    )
    not_found_trans = are_all_kws_present(kws, word_freq_trans)
    if not_found_trans:
        print("Missed keywords in {:s}".format(args.test_trans_f), not_found_trans)
    else:
        print("Found all unique keywords")

    # ------ RTTM 1 --------

    word_freq_rttm1, kw_ts_rttm1 = get_unique_words_from_rttm(args.rttm_1, kws)
    print(
        "Found {:d} unique words in RTTM {:s}".format(
            len(word_freq_rttm1), args.rttm_1
        ),
        end="\t -- ",
    )
    not_found_rttm1 = are_all_kws_present(kws, word_freq_rttm1)
    if not_found_rttm1:
        print("Missed keywords in {:s}".format(args.rttm_1), not_found_rttm1)
    else:
        print("Found all unique keywords")

    flag_1 = compare_wfreqs(kws, word_freq_trans, word_freq_rttm1)

    # ----------- RTTM 2 -------------

    word_freq_rttm2, kw_ts_rttm2 = get_unique_words_from_rttm(args.rttm_2, kws)

    print(
        "Found {:d} unique words in RTTM {:s}".format(
            len(word_freq_rttm2), args.rttm_2
        ),
        end="\t -- ",
    )
    not_found_rttm2 = are_all_kws_present(kws, word_freq_rttm2)
    if not_found_rttm2:
        print("Missed keywords in {:s}".format(args.rttm_2), not_found_rttm2)
    else:
        print("Found all unique keywords")

    flag_2 = compare_wfreqs(kws, word_freq_trans, word_freq_rttm1)

    # ---- Compare time stamps of both RTTMs files for all the keywords

    # if (
    #     len(not_found_rttm1) + len(not_found_rttm2) > 0
    #     or flag_1 is False
    #     or flag_2 is False
    # ):
    #     print(
    #         "Will not compare the time stamps in both RTTMs because some keywords are missing in RTTM file(s)."
    #     )
    # sys.exit()

    print("\nComparing start and end time stamps for keywords from both the RTTMs ..\n")

    flag = True
    for utt_id in kw_ts_rttm1:
        if utt_id not in kw_ts_rttm2:
            print(
                "  Utt_id {:s} found in {:s} but not in {:s}".format(
                    utt_id, args.rttm_1, args.rttm_2
                )
            )
            flag = False

        else:
            sub_1 = kw_ts_rttm1[utt_id]
            sub_2 = kw_ts_rttm1[utt_id]
            if len(sub_1) != len(sub_2):
                print("  Mismatch:", utt_id, sub_1, sub_2)
                flag = False
            for kw in sub_1:
                for i, ts in enumerate(sub_1[kw]):
                    if abs(ts - sub_2[kw][i]) > args.tol:
                        print("  Mismatch:", utt_id, kw, sub_1[kw], sub_2[kw])
                        flag = False

    if flag:
        print(
            "  Start and end time stamps for all the keywords match (with tolerance {:.2f} s) in both RTTMs.\n".format(
                args.tol
            )
        )


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("rttm_1", help="path to first rttm file")
    parser.add_argument("rttm_2", help="path to second rttm file")
    parser.add_argument("keywords_f", help="path to keywords.txt")
    parser.add_argument("test_trans_f", help="path to test transcription file")
    parser.add_argument(
        "-tol",
        type=float,
        default=0.01,
        help="tolerance for start and end time stamp comparison",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
