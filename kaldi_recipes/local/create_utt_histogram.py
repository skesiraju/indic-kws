#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 03 Jun 2021
# Last modified : 03 Jun 2021

"""
Get total duration on utterances. If input is utt2dur, the calculation
is straightforward. If the input is wav.scp then will use sox command
to get the duration of each recording.
"""

import os
import sys
import argparse
from random import shuffle
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from make_train_dev_test_splits import get_uid2dur_mapping, load_key_value_from_text, get_utt2uid_mapping


def main():
    """ main method """

    args = parse_arguments()

    utt2uid = {}  # utterance text to utterance ID mapping
    uid2dur = {}  # utterance ID to duration mapping

    for set_name in ["train", "test"]:

        if args.set_name != "both":
            if args.set_name != set_name:
                continue

        print("processing", set_name, "set ..")

        text_f = os.path.join(args.data_dir, f"{set_name}/text")

        utt2uid = get_utt2uid_mapping(text_f, utt2uid)

        uid2dur = get_uid2dur_mapping(args.data_dir, f"{set_name}", uid2dur)

    uid2text = {}
    for text, uids in utt2uid.items():
        for uid in uids:
            uid2text[uid] = text

    print(
        "# utt2uid:",
        len(utt2uid),
        " |  # uid2text:",
        len(uid2text),
        "|  # uid2dur:",
        len(uid2dur),
    )

    cntbin2uids = (
        {}
    )  # nested dict {bin_1: {utt_11: [uid_11]..}, bin_2: {utt_22: [uid_221, uid_222], ...}, ...}
    utt2avgdur = {}
    avg_uniq_dur = 0.0

    for utt, uids in utt2uid.items():
        n_uids = len(uids)
        sub_dict = {}
        if n_uids in cntbin2uids:
            sub_dict = cntbin2uids[n_uids]
        sub_dict[utt] = uids
        cntbin2uids[n_uids] = sub_dict

        utt_avg_dur = 0.0
        for uid in uids:
            utt_avg_dur += uid2dur[uid]
        utt_avg_dur /= len(uids)
        utt2avgdur[utt] = utt_avg_dur
        avg_uniq_dur += utt_avg_dur

    n_utts = 0
    for i in cntbin2uids:
        n_utts += i * len(cntbin2uids[i])
    print("# utts:", n_utts)

    total_dur = 0.0
    for uid, dur in uid2dur.items():
        total_dur += dur

    print("total dur: {:.2f} hrs".format(total_dur / 3600))
    print("uniq utt dur: {:.2f} hrs".format(avg_uniq_dur / 3600))

    cnt_bins = [len(sub_dict) for k, sub_dict in cntbin2uids.items()]

    plt.figure(1)
    plt.hist(cnt_bins, bins=np.arange(1, max(cnt_bins)+1, 1))
    plt.grid(linestyle='--', alpha=0.5)
    plt.show()


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("data_dir", help="path to data dir")
    parser.add_argument(
        "-set_name", choices=["train", "test", "both"], default="both", type=str
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
