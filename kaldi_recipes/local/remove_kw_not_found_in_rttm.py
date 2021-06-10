#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Santosh
# e-mail : kcraj2[AT]gmail[DOT]com
# Date created : 02 Apr 2021
# Last modified : 02 Apr 2021

"""
"""

import os
import sys
import argparse

def main():
    """ main method """

    args = parse_arguments()

    not_found = set()
    with open(args.rttm_out_file, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            if line.strip():
                not_found.add(line.strip().split()[-1])
    print("not found in rttm", len(not_found))

    if len(not_found) == 0:
        sys.exit()

    kws = []
    with open(args.kw_file, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            word = line.strip().split()[-1]
            if word in not_found:
                continue
            kws.append(word)

    with open(args.kw_file, 'w', encoding='utf-8') as fpw:
        for i, k in enumerate(kws):
            fpw.write(str(i+1) + " " + k + "\n")
    print("Updated", args.kw_file)


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kw_file")
    parser.add_argument("rttm_out_file")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
