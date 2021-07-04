#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author : Santosh Kesiraju
# e-mail : kcraj2[AT]gmail[DOT]com, kesiraju[AT]fit[DOT]vutbr[DOT]cz
# Date created : 25 Jan 2021
# Last modified : 25 Jan 2021

"""
Extract documents from the extracted wiki xml text files.
"""

import os
import re
import sys
import argparse
import glob
import tqdm
from pylibs.misc.io import write_simple_flist


def parse_file(xfile):

    docs = {}  # doc_id: [text]
    content = u""

    patt = re.compile(r"id=\"[0-9]+\"")

    with open(xfile, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            line = line.strip()
            if not line:
                continue

            if line.startswith("<doc"):
                # start of a document
                doc_id = patt.findall(line)[0][4:-1]

            elif line.startswith("</doc>"):
                # end of the document
                docs[doc_id] = content
                content = u""

            else:
                # content of the document
                content += line + "\n"

    return docs


def main():
    """ main method """

    args = parse_arguments()

    os.makedirs(args.out_dir, exist_ok=True)

    files = glob.glob(args.in_text_dir + "/*/wiki*")

    n_docs = 0

    for xfile in tqdm.tqdm(files):
        # print("\rProcessing {:6d} / {:6d} {:9d} docs found".format(i+1, len(files), n_docs), end=" ")

        x_docs = parse_file(xfile)
        n_docs += len(x_docs)

        for doc_id in x_docs:
            with open(os.path.join(args.out_dir, doc_id + ".txt"), "w", encoding="utf-8") as fpw:
                fpw.write(x_docs[doc_id])

            with open(os.path.join(args.out_dir, "../", "raw_data.txt"), "a", encoding="utf-8") as fpw:
                fpw.write(x_docs[doc_id] + "\n")

    print("\nSaved in", args.out_dir)



def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_text_dir", help="path to text dir where all the input files are present (in sub-dirs)")
    parser.add_argument("out_dir", help="path to output dir, where documents will be stored")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
