#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 29 Jun 2021
# Last modified : 29 Jun 2021

"""
merge two keywords files into a single out file, with proper numbering
"""

import os
import sys
from glob import glob
import argparse
from auto_utils import load_keywords, write_kw_to_file


def main():
    """ main method """

    args = parse_arguments()

    kw_files = glob(args.kw_dir + args.prefix + "*")
    all_kws = set()
    for kw_file in kw_files:
        kw1 = load_keywords(kw_file)
        all_kws |= kw1

    print("all kws:", len(all_kws))

    write_kw_to_file(list(all_kws), args.out_file)



def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("kw_dir", help="dir with kw files")
    parser.add_argument("prefix", type=str, help="common file prefix")
    parser.add_argument("out_file", help="out file to save")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
