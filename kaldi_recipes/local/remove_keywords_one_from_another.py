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
import argparse
from auto_utils import load_keywords, write_kw_to_file


def main():
    """ main method """

    args = parse_arguments()

    kw1 = load_keywords(args.kw_file1)
    kw2 = load_keywords(args.kw_file2)

    kw2_minus_kw1 = kw2 - kw1

    print("kw1:", len(kw1), "kw2:", len(kw2), "kw2 - kw1:", len(kw2_minus_kw1))

    write_kw_to_file(list(kw2_minus_kw1), args.out_file)



def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("kw_file1", help="these will be removed (small sub set)")
    parser.add_argument("kw_file2", help="from these (super set)")
    parser.add_argument("out_file", help="out file to save final keywords")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
