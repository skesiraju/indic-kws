#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 01 Jul 2021
# Last modified : 01 Jul 2021

"""
Extract unique utts (lexical content) and save one/or more utt ID - utt
"""

import os
import sys
import argparse
import numpy as np
from make_train_dev_test_splits import (
    get_utt2uid_mapping,
    get_uid2dur_mapping,
    load_key_value_from_text,
)
from auto_utils import get_word_count, get_wfreq, arrange_into_freq_bins


def main():
    """ main method """

    args = parse_arguments()

    files_to_filter = [
        "feats.scp",
        "wav.scp",
        "cmvn.scp",
        "segments",
        "dur.txt",
        "spk2utt",
        "utt2spk",
        "utt2dur",
        "text",
        "utt2num_frames",
    ]
    files_to_copy = ["frame_shift", ".mfcc.done"]

    data_dir = args.data_dir

    for set_name in ["dev", "test"]:

        text = os.path.join(data_dir, f"{set_name}/text")
        utt2uid = {}
        utt2uid = get_utt2uid_mapping(text, utt2uid)

        uid2dur = {}
        ui2dur = get_uid2dur_mapping(data_dir, set_name, uid2dur)

        print(set_name, "utt2uid:", len(utt2uid))

        utt2_num_uids = {}
        for utt in utt2uid:
            utt2_num_uids[utt] = len(utt2uid[utt])
        print(set_name, "utt2num_uids:", len(utt2_num_uids))

        utts = list(utt2uid.keys())

        wc1 = {}
        wc1 = get_word_count(utts, wc1)
        print(set_name, "wc1:", len(wc1))
        counts1 = get_wfreq(wc1)
        arrange_into_freq_bins(counts1, 25)

        counts3 = get_wfreq(utt2_num_uids)
        # arrange_into_freq_bins(counts3, 100)
        avg_uids = int(np.mean(counts3))
        print(
            "avg uids per utt (thresh):",
            avg_uids,
            "min:",
            np.min(counts3),
            "max:",
            np.max(counts3),
        )

        selected_uids = []
        selected_utts = []
        more_than_thresh = 0
        less_than_thresh = 0
        for utt, uids in utt2uid.items():
            rand_num = np.random.randint(1, args.max_num + 1, 1)[0]
            if len(uids) > avg_uids:
                for i, uid in enumerate(uids):
                    selected_uids.append(uid)
                    selected_utts.append(utt)
                    more_than_thresh += 1
                    if i >= rand_num:
                        break
            else:
                selected_uids.append(uids[0])
                selected_utts.append(utt)
                less_than_thresh += 1

        uniq_dur = 0.0
        for utt in set(selected_utts):
            uniq_dur += uid2dur[utt2uid[utt][0]]
        selected_dur = 0.0
        for uid in selected_uids:
            selected_dur += uid2dur[uid]
        print(
            "selected dur : {:.1f} hr, unique dur: {:.1f}".format(
                (selected_dur / 3600.0), (uniq_dur / 3600.0)
            )
        )

        print(
            "selected uids:",
            len(selected_uids),
            "more than thresh:",
            more_than_thresh,
            "less than thresh:",
            less_than_thresh,
        )
        print("selected utts:", len(selected_utts))

        wc2 = {}
        wc2 = get_word_count(selected_utts, wc2)
        print(set_name, "wc2:", len(wc2))
        counts2 = get_wfreq(wc2)
        arrange_into_freq_bins(counts2, 25)

        target_dir = os.path.join(data_dir, f"{set_name}_{args.target_sfx}/")
        os.makedirs(target_dir, exist_ok=True)
        print("* Traget dir:", target_dir)

        for base in files_to_filter:
            in_file = os.path.join(data_dir, f"{set_name}/{base}")
            if not os.path.exists(in_file):
                continue
            id2text = {}
            id2text = load_key_value_from_text(in_file, id2text, full_line=True)

            out_file = os.path.join(target_dir, base)
            with open(out_file, "w", encoding="utf-8") as fpw:
                for uid in sorted(selected_uids):
                    fpw.write(id2text[uid].strip() + "\n")
            print(out_file, "saved.")

        for base in files_to_copy:
            in_file = os.path.join(data_dir, f"{set_name}/{base}")
            if not os.path.exists(in_file):
                continue
            os.system(f"cp {in_file} {target_dir}/")
            print(target_dir + "base copied.")

        uids_fname = os.path.join(target_dir, f"{set_name}.ids")
        with open(uids_fname, "w") as fpw:
            for uid in selected_uids:
                fpw.write(uid + "\n")
        print(uids_fname, 'saved.')

        print()


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("target_sfx", type=str, help="sfx to identify the target dir")
    parser.add_argument("-data_dir", default="data/", type=str, help="path to data dir")
    parser.add_argument(
        "-max_num",
        type=int,
        default=5,
        help="max number of uids per utt to take, if they are more than threshold.\
in reality a random number is picked between 1 and max_num",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
