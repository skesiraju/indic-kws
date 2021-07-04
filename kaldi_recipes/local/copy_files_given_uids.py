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
    set_name = os.path.dirname(data_dir).split("/")[-1]
    print("set_name:", set_name)

    # sys.exit()

    selected_uids = []
    with open(args.uids_file, 'r') as fpr:
        for line in fpr:
            selected_uids.append(line.strip())

    print("uids:", len(selected_uids))

    target_dir = args.target_dir
    os.makedirs(target_dir, exist_ok=True)

    for base in files_to_filter:
        in_file = os.path.join(data_dir, f"{base}")
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
        in_file = os.path.join(data_dir, f"{base}")
        if not os.path.exists(in_file):
            continue
        os.system(f"cp {in_file} {target_dir}/")


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("uids_file", help="path to file with utt ids")
    parser.add_argument("data_dir", type=str, help="path to data dev or test dir")
    parser.add_argument("target_dir", help="path to target dir")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
