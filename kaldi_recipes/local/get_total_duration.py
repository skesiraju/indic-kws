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
import subprocess


def main():
    """ main method """

    args = parse_arguments()

    in_file = args.utt2dur if args.utt2dur else args.wavscp

    total_dur = 0.0
    with open(in_file, 'r', encoding='utf-8') as fpr:
        lno = 0
        for line in fpr:
            lno += 1
            parts = line.strip().split()
            if len(parts) != 2:
                print("Each line should have two columns. Found:", parts, "at line", lno,
                      file=sys.stderr)
                sys.exit()

            if args.utt2dur:
                total_dur += float(parts[1])
            elif args.wavscp:
                res = subprocess.run(["soxi", "-D", parts[1]], capture_output=True)
                total_dur += float(res.stdout)

    print("Total duration: {:.2f} sec = {:.2f} min = {:.2f} hr".format(
        total_dur, total_dur / 60., total_dur/3600.))

def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    me_group = parser.add_mutually_exclusive_group(required=True)

    me_group.add_argument("-utt2dur", default="", help="path to utt2dur file")
    me_group.add_argument("-wavscp", default="", help="path to wav.scp file")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
