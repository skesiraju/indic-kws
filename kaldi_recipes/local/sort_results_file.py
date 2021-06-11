#!/usr/bin/env python3

import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("results_file")
args = parser.parse_args()

header = ""
with open(args.results_file, "r") as fpr:
    header = fpr.readline()
    
res = np.loadtxt(args.results_file)

sort_ixs = np.argsort(res[:, 0])

with open(args.results_file + "_sorted", "w") as fpw:
    fpw.write(header)
    for i in sort_ixs:
        fpw.write(str(int(res[i, 0])) + " " + str(res[i, 1]) + "\n")
print(args.results_file + "_sorted")
