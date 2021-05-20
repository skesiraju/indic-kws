#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 25 Mar 2021
# Last modified : 25 Mar 2021

"""
"""

import os
import sys
import argparse



def main():
    """ main method """

    args = parse_arguments()

    flist = {}
    with open(args.orig_flist, "r") as fpr:
        for line in fpr:
            # print(line)
            fname = line.strip()
            base = os.path.basename(fname).rsplit(".", 1)[0]
            if base in flist:
                print("strage:", base, fname)
            else:
                flist[base] = fname

    print("# wav files:", len(flist))

    utt_ids = []
    file_path = []
    with open(args.scp_file, "r") as fpr:
        for line in fpr:
            parts = line.strip().split()
            utt_ids.append(parts[0])

    print("# utt ids  :", len(utt_ids))

    os.system(f"cp {args.scp_file} {args.scp_file}.bak")

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
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("scp_file")
    parser.add_argument("orig_flist")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
