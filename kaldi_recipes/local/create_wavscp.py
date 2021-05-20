#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 25 Mar 2021
# Last modified : 25 Mar 2021

"""
--------------------------------------------------------------
Create wav.scp given a file with `list of wave file paths`

orig_flist can be created by the following bash commad

find `realpath Hindi/train` -name "*.wav" > hindi_train.flist
--------------------------------------------------------------
"""

import os
import sys
import argparse



def main():
    """ main method """

    args = parse_arguments()

    utt_ids = []
    flist = {}
    with open(args.orig_flist, "r") as fpr:
        for line in fpr:
            # print(line)
            fname = line.strip()
            base = os.path.basename(fname).rsplit(".", 1)[0]
            if base in flist:
                print(f"{base} already found in dict.", fname, flist[base])
            else:
                flist[base] = fname
                utt_ids.append(base)

    print("# wav files:", len(flist))

    utt_ids = sorted(utt_ids)

    print("# utt ids  :", len(utt_ids))

    with open(args.scp_file, "w") as fpw:
        for utt_id in utt_ids:
            try:
                fpw.write(utt_id + " " + flist[utt_id] + "\n")
            except KeyError:
                print(utt_id, "not found.")


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("orig_flist", help="input wav flist file")
    parser.add_argument("scp_file", help="output wavscp file")
    args = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
    return args

if __name__ == "__main__":
    main()
