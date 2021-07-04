#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 15 Mar 2021
# Last modified : 15 Mar 2021

"""
Clean the data
"""

import os
import sys
import argparse
import string
from tqdm import tqdm


UNICODE = {
    "tel": [0x0c00, 0x0c7f],
    "tam": [0x0b80, 0x0bff],
    "guj": [0x0a80, 0x0aff],
    "hin": [0x0900, 0x097f],
    "mar": [0x0900, 0x097f],
    "ori": [0x0b00, 0x0b7f]
    }


def validate_unicode_range(range_string):
    """ Validate the unicode range given as colon and comma separated string """

    uni_ranges = []

    ranges = range_string.split(",")

    if len(ranges) > 2:
        print("Maximum two unicode ranges can be given.", file=sys.stderr)
        sys.exit()

    for rng in ranges:
        parts = rng.split(":")
        if len(parts) != 2:
            print(
                "unicode_range: start and end values must be separated by a comma.",
                file=sys.stderr,
            )
            sys.exit()

        try:
            uni_start = int(parts[0], 16)
            uni_end = int(parts[1], 16)
            uni_ranges.append([uni_start, uni_end])
        except ValueError:
            print(
                "unicode_range: start and end values must be hexadecimal.", file=sys.stderr
            )
            sys.exit()

    return sorted(uni_ranges)


def main():
    """ main method """

    args = parse_arguments()

    # uni_ranges = validate_unicode_range(args.uni_ranges)
    uni_ranges = UNICODE[args.lang]

    # if args.ascii:

    #     present = False
    #     for uni_range in uni_ranges:
    #         if uni_range[0] == 0 and uni_range[1] == 127:
    #             present = True
    #     if not present:
    #         uni_ranges.append([0, 127])

    #     uni_ranges = sorted(uni_ranges)

    print("Min number of tokens per line:", args.misl)
    print("Max word length              :", args.mxwl)
    print("Remove punctuation           :", args.remove_punc)
    print("Unicode ranges               :", uni_ranges)

    with open(args.in_text_file, 'r', encoding='utf-8') as fpr:
        lines = fpr.readlines()

    punc = str.maketrans('', '', string.punctuation)

    cleaned_lines = []

    for line in tqdm(lines):

        if args.remove_punc:
            line = line.translate(punc).strip()

        cleaned_line = ""
        tokens = line.strip().split()

        if len(tokens) >= args.misl:
            for tok in tokens:
                if len(tok) <= args.mxwl:
                    flag = True
                    for c in tok:
                        #if uni_ranges[0][0] <= ord(c) <= uni_ranges[0][1] or uni_ranges[1][0] <= ord(c) <= uni_ranges[1][1]:
                        if uni_ranges[0] <= ord(c) <= uni_ranges[1]:
                            continue
                        else:
                            flag = False
                            break
                    if flag and tok.strip():
                        cleaned_line += tok.strip()  + " "

        if cleaned_line.strip():
            # print(line, " -> ", cleaned_line)
            cleaned_lines.append(cleaned_line.strip())

    with open(args.out_text_file, "w", encoding="utf-8") as fpw:
        fpw.write("\n".join(cleaned_lines))
    print("Done !!")


def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "in_text_file", help="path to input text file that needs to be cleaned"
    )
    parser.add_argument("lang", choices=["guj", "tam", "tel", "hin", "mar", "ori"])
    parser.add_argument("out_text_file", help="path to cleaned output text file")
    parser.add_argument(
        "-misl", type=int, default=1, help="minimum number of tokens in a sentence"
    )
    parser.add_argument(
        "-mxwl", type=int, default=30, help="maximum number of characters in a word"
    )
    parser.add_argument(
        "--remove_punc",
        action="store_true",
        help="removes punctuation, replaced with empty character",
    )
    # parser.add_argument(
    #    "--remove_num",
    #    action="store_true",
    #    help="removes numerals, replaced with empty character",
    #)
#     parser.add_argument(
#         "-uni_ranges",
#         default="0x0000,0x007f",
#         help="unicode start and end range (colon-separated hexadecimal values). \
# Two different ranges can be given by separating with a comma , (0x0000:0x00ff,0x0400:0x04ff). \
# Only characters in this range will be considered. Can be used in conjunction with --ascii",
#     )
#     parser.add_argument(
#         "--ascii",
#         action="store_true",
#         help="ascii characters 0-127 will also be considered apart from -uni_range",
#     )
    parser.add_argument("-nj", type=int, default=1, help="number of parallel jobs")
    args = parser.parse_args()


    return args


if __name__ == "__main__":
    main()
