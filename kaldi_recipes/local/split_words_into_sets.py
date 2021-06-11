#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Santosh
# e-mail : kcraj2[AT]gmail[DOT]com
# Date created : 04 Apr 2021
# Last modified : 04 Apr 2021

"""
"""

import os
import sys
import argparse
from auto_utils import load_keywords


def main():
    """ main method """

    args = parse_arguments()

    os.makedirs(args.out_dir, exist_ok=True)
    words = load_keywords(args.input_file)
    words = sorted(list(words))
    print("Loaded", len(words), "words.")

    fname = ""
    fpw = None
    j = 0
    k = 1
    for i, w in enumerate(words):
        if (i % args.num == 0):
            if fpw:
                fpw.close()
                print("{:4d}".format(j), "words saved in", fname)
                j = 0

            fname = os.path.join(args.out_dir, f"set_{k}.txt")
            fpw = open(fname, "w", encoding="utf-8")
            k += 1

        j += 1
        fpw.write(str(j) + " " + w + "\n")


    fpw.close()
    print("{:4d}".format(j), "words saved in", fname)


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", help="input file with just words")
    parser.add_argument("num", type=int, help="max number of words per split")
    parser.add_argument("out_dir", help="dir to save the splits")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
