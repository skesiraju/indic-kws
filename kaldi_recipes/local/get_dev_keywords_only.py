#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Santosh
# e-mail : kcraj2[AT]gmail[DOT]com
# Date created : 28 Mar 2021
# Last modified : 28 Mar 2021

"""
"""

import os
import sys
import argparse

def main():
    """ main method """

    args = parse_arguments()

    all_kw = set()
    with open(args.all_keywords_file, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            word = line.strip().split()[1]
            all_kw.add(word)
    print('# all kw:', len(all_kw))

    dev_kw = set()
    with open(args.dev_text, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            tokens = line.strip().split()[1:]
            for tok in tokens:
                if tok in all_kw:
                    dev_kw.add(tok)
    print("# dev kw:", len(dev_kw))

    dev_kw = list(dev_kw)
    with open(args.out_keywords_file, 'w', encoding='utf-8') as fpw:
        for i, kw in enumerate(dev_kw):
            fpw.write(str(i+1) + " " + kw + "\n")
    print(args.out_keywords_file, "saved.")





def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("all_keywords_file")
    parser.add_argument("dev_text")
    parser.add_argument("out_keywords_file")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
