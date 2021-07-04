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


def get_uid2dur_mapping(data_dir, set_name, uid2dur):
    """ Get utterance ID to duration (sec) mapping """

    utt2dur_f = os.path.join(data_dir, f"{set_name}/utt2dur")
    wavscp_f = os.path.join(data_dir, f"{set_name}/wav.scp")

    if os.path.exists(utt2dur_f):
        with open(utt2dur_f, "r", encoding="utf-8") as fpr:
            for line in fpr:
                parts = line.strip().split()
                if len(parts) != 2:
                    print(
                        "Each line should have two columns. Found:",
                        parts,
                        "at line",
                        lno,
                        file=sys.stderr,
                    )
                    sys.exit()
                uid2dur[parts[0]] = float(parts[1])

    elif os.path.exists(wavscp_f):
        with open(wavscp_f, "r", encoding="utf-8") as fpr:
            for line in fpr:
                parts = line.strip().split()
                res = subprocess.run(["soxi", "-D", parts[1]], capture_output=True)
                uid2dur[parts[0]] = float(res.stdout)

    return uid2dur


def load_key_value_from_text(fname, id2text, full_line=True):

    with open(fname, "r", encoding="utf-8") as fpr:
        for line in fpr:
            parts = line.strip().split(" ", 1)
            if parts[0] not in id2text:
                if full_line:
                    id2text[parts[0]] = line.strip()
                else:
                    id2text[parts[0]] = parts[1].strip()

            else:
                print("Duplicate ID:", parts[0])
                sys.exit()

    return id2text


def save_subset(in_files, out_ids, out_file):

    id2text = {}
    for in_file in in_files:
        id2text = load_key_value_from_text(in_file, id2text, True)
    with open(out_file, "w", encoding="utf-8") as fpw:
        for uid in sorted(out_ids):
            fpw.write(id2text[uid].strip() + "\n")

    print(out_file, "saved.")


def get_utt2uid_mapping(text_f, utt2uid):

    lno = 0
    with open(text_f, "r", encoding="utf-8") as fpr:
        for line in fpr:
            lno += 1
            uid, text = line.strip().split(" ", 1)
            if text in utt2uid:
                utt2uid[text].append(uid)
            else:
                utt2uid[text] = [uid]
    return utt2uid


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

    import ipdb
    ipdb.set_trace()

    desired_total_dur = 5 * 3600.0
    desired_uniq_dur = avg_uniq_dur * 0.15
    print(
        "desired uniq utt dur for each dev and test sets: {:.2f} min".format(
            desired_uniq_dur / 60.0
        )
    )

    bin_sizes = []
    for i in range(500):
        if i not in cntbin2uids:
            bin_sizes.append(0)
        else:
            bin_sizes.append(len(cntbin2uids[i]))


    selected_utts = {"dev": set(), "test": set()}
    selected_uids = {"dev": [], "test": []}
    selected_set = set()
    percent = args.percent

    for set_name in ["dev", "test"]:

        obt_dur = 0.0
        cntbin_thresh = 1
        flag = False

        while obt_dur < desired_uniq_dur:
            for i in range(500):
                if i not in cntbin2uids:
                    continue
                sub_dict = cntbin2uids[i]
                max_utts_per_bin = int(len(sub_dict) * percent)
                j = 0
                for utt in sub_dict:
                    if utt in selected_set:
                        continue

                    obt_dur += utt2avgdur[utt]
                    selected_utts[set_name].add(utt)
                    selected_set.add(utt)
                    j += 1
                    if obt_dur > desired_uniq_dur:
                        flag = True
                        break
                    if j > max_utts_per_bin:
                        print(
                            "{:2d} {:4d} {:6.2f}/{:6.2f}".format(
                                i,
                                len(selected_utts[set_name]),
                                obt_dur,
                                desired_uniq_dur,
                            )
                        )
                        break

                if flag:
                    break

        set_dur = 0.
        set_uids = []
        for utt in selected_utts[set_name]:
            for uid in utt2uid[utt]:
                set_dur += uid2dur[uid]
                set_uids.append(uid)
        selected_uids[set_name] = sorted(set_uids)
        print(set_name, "dur: {:.2f}".format(set_dur/3600.))

        if args.set_name == 'train':
            break

    print('utts in dev + test:', len(selected_set))

    all_uids = set(list(uid2dur.keys()))

    train_set = all_uids - (set(selected_uids['dev']) | set(selected_uids['test']))
    train_uids = sorted(list(train_set))
    print(len(all_uids), len(train_uids), len(selected_uids['dev']), len(selected_uids['test']))

    os.makedirs(args.out_dir, exist_ok=True)

    dev_dur = 0.0
    for uid in selected_uids['dev']:
        dev_dur += uid2dur[uid]
    print("Dev dur: {:.1f}".format(dev_dur / 3600))

    if os.path.exists(os.path.join(args.out_dir, "/train/text")):
        print("Files present in", args.out_dir)
        sys.exit()
    else:
        with open(
            os.path.join(args.out_dir, "train.ids"), "w", encoding="utf-8"
        ) as fpw:
            for uid in train_uids:
                fpw.write(uid + "\n")

        with open(os.path.join(args.out_dir, "dev.ids"), "w", encoding="utf-8") as fpw:
            for uid in selected_uids['dev']:
                fpw.write(uid + "\n")

        if selected_uids['test']:
            with open(os.path.join(args.out_dir, "test.ids"), "w", encoding="utf-8") as fpw:
                for uid in selected_uids['test']:
                    fpw.write(uid + "\n")

    uids = {"train": train_uids, "dev": selected_uids['dev'], "test": selected_uids['test']}
    for set_name in ["train", "dev", "test"]:
        os.makedirs(args.out_dir + "/" + set_name, exist_ok=True)
        for base in ["text", "utt2spk", "wav.scp"]:
            main_f = [args.data_dir + f"train/{base}", args.data_dir + f"test/{base}"]
            out_f = args.out_dir + f"/{set_name}/{base}"
            if uids[set_name]:
                save_subset(main_f, uids[set_name], out_f)


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("data_dir", help="path to data dir")
    parser.add_argument("out_dir", help="path to out dir to save new splits")
    parser.add_argument("-percent", type=float, default=0.15, help="percentage of dev and test")
    parser.add_argument(
        "-set_name", choices=["train", "test", "both"], default="both", type=str
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
