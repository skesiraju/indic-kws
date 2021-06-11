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
import numpy as np
import matplotlib.pyplot as plt


def load_res_and_sort(res_file):

    res = np.loadtxt(res_file)
    sort_ixs = np.argsort(res[:, 0])
    return res[sort_ixs, :]


def main():
    """ main method """

    args = parse_arguments()

    wlen_res = load_res_and_sort(args.wlen_res_file)
    wfreq_res = load_res_and_sort(args.wfreq_res_file)
    conf_res = load_res_and_sort(args.conf_res_file)

    print(wlen_res.shape)
    print(wfreq_res.shape)
    print(conf_res.shape)

    _, axs = plt.subplots(ncols=3, figsize=(9, 4))

    axs[0].set_title("wlen")
    axs[0].plot(wlen_res[:, 0], wlen_res[:, 1], '.-')
    axs[0].set_xticks(wlen_res[:, 0].astype(int))

    axs[1].set_title("wfreq")
    axs[1].plot(wfreq_res[:, 0], wfreq_res[:, 1], '.-')
    axs[1].set_xticks(wfreq_res[:, 0].astype(int))

    axs[2].set_title("kw conf")
    axs[2].plot(conf_res[:, 0], conf_res[:, 1], '.-')
    axs[2].set_xticks(conf_res[:, 0].astype(int))

    for ax in axs:

        ax.grid()
        ax.set_ylabel('ATWV')

    plt.tight_layout()
    plt.show()



def parse_arguments():
    """ parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wlen_res_file")
    parser.add_argument("wfreq_res_file")
    parser.add_argument("conf_res_file")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
