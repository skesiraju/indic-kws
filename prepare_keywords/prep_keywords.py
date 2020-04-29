#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author: Santosh
# date: 22 April 2020

"""
Prepare set of keywords by using various criteria, statistics and given options
"""

import os
import sys
import ipdb
import codecs
import argparse
from collections import OrderedDict
from multiprocessing import Pool
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
from Levenshtein import distance  # pylint: disable=no-name-in-module


def distance_words(word, w2i):
    """ Return row of distances from word to subsequent words in w2i """

    dist = np.zeros(shape=(len(w2i) - w2i[word]), dtype=np.uint8)
    for w, i in w2i.items():
        if i >= w2i[word]:
            dist[i-w2i[word]] = distance(word, w)
    return dist


def compute_dist_matrix(w2i, njobs=1):
    """ Compute distance matrix """

    dist_matrix = np.zeros(shape=(len(w2i), len(w2i)),
                           dtype=np.uint8)
    print("Computing distance matrix of size:", dist_matrix.shape,
            "Takes time.....")

    words = [w for w in sorted(w2i, key=w2i.get)]
    dist_fn = partial(distance_words, w2i=w2i)
    for i, word in enumerate(words):
        print("\rRow {:6d}/{:6d}".format(i+1, len(words)), end="")
        dist_matrix[i, i:] = dist_fn(word)
    print()

    # the above step can be parallelized
    # but there's some error: function can't be pickled.
    # ToDo: fix it
    # with Pool(njobs) as pool:
    #    dist_list = pool.map(dist_fn, words)

    return dist_matrix


class KeywordFilter:
    """ Keyword filter """

    def __init__(self, lang, sim_len=1, wlen=3):
        """ Initialize KeywordFilter """

        self.lang = lang
        self.sim_len = sim_len
        self.wlen = wlen
        # self.wfreq = wfreq

        self.lex = OrderedDict()
        self.w2i = OrderedDict()

        self.ignore_words = {'!SIL', '<UNK>'}

    def load_lexicon(self, lex_fname):
        """ Load lexicon into dictionary where key is word and
        value is phone seq. Additionally return word to integer mapping """

        with codecs.open(lex_fname, 'r', 'utf-8') as fpr:
            for line in fpr:
                parts = line.strip().split()
                word = parts[0]
                if word in self.ignore_words:
                    continue
                phn_seq = parts[1:]

                if word in self.lex:
                    print("Error: word", word, "already present in lexicon.")
                    sys.exit()

                self.lex[word] = phn_seq
                self.w2i[word] = len(self.w2i)

    def filter_kw_wlen(self, plot, fig_name):
        """ Filter keywords based on word length (number of phones) """

        word_lengths = np.zeros(shape=(len(self.lex),), dtype=np.uint8)
        words = []

        for w, phn_seq in self.lex.items():
            word_lengths[self.w2i[w]] = len(phn_seq)
            if len(phn_seq) == self.wlen:
                words.append(w)

        if plot:
            plt.figure(1, figsize=(8, 6))
            plt.xticks(np.arange(np.max(word_lengths)))
            plt.xlabel('Word length (number of phones)')
            plt.ylabel('Number of words')
            plt.hist(word_lengths, bins=np.max(word_lengths))
            plt.grid(alpha=0.3, linestyle='--')
            plt.savefig(fig_name, dpi=300)
            plt.show()

        return words

    def filter_similar_words(self, plot, out_dir, fig_name, njobs=8):
        """ Filter similar words based on Levenshtein distance """

        words = list(self.w2i.keys())

        # distance matrix between every word
        # this matrix will be symmetric with zeros along the diagonal
        dist_matrix_file = f"{out_dir}/{self.lang}_leven_dist_matrix.npz"
        if os.path.exists(dist_matrix_file):
            print("Loading existing distance matrix:", dist_matrix_file)
            dist_matrix = np.load(dist_matrix_file)['arr_0']

        else:
            dist_matrix = compute_dist_matrix(self.w2i, njobs=njobs)
            np.savez_compressed(dist_matrix_file, dist_matrix)
            print('Similarity matrix saved for future use:', dist_matrix_file)

        ixs = np.where(dist_matrix == self.sim_len)

        word_pairs = ([], [])
        # for each word_ix, count the number of similar words
        word_ix_dict = OrderedDict()
        for i, j in zip(*ixs):
            try:
                word_ix_dict[i] += 1
            except KeyError:
                word_ix_dict[i] = 1
            word_pairs[0].append(words[i])
            word_pairs[1].append(words[j])

        if plot:
            counts = np.asarray(list(word_ix_dict.values()), dtype=np.uint16)
            plt.figure(2, figsize=(8, 6))
            # plt.xticks(np.arange(np.max(counts)))
            plt.xlabel('Number of similar words')
            plt.ylabel('Number of words')
            plt.hist(counts, bins=np.max(counts))
            plt.grid(alpha=0.3, linestyle='--')
            plt.savefig(fig_name, dpi=300)
            plt.show()

        return word_pairs

    def apply_12(self, words_f1, word_pairs_f2):
        """ Apply both the filters and obtain common words """

        inter_pairs = ([], [])
        words_f1 = set(words_f1)

        for i, w in enumerate(word_pairs_f2[0]):
            if w in words_f1:
                inter_pairs[0].append(w)
                inter_pairs[1].append(word_pairs_f2[1][i])

        return inter_pairs

    def filter_based_on_freq(self, train_file, test_file=None, plot=False):
        """ Filter words based on their frequency of occurrence """



        ipdb.set_trace()


def get_vocab_and_seg_ids(fname, vocab=None, seg_ids=None):
    """ return dict of vocab and seg ids """

    if vocab is None:
        vocab = OrderedDict()
    if seg_ids is None:
        seg_ids = OrderedDict()

    with codecs.open(fname, 'r', 'utf-8') as fpr:
        for line in fpr:
            parts = line.strip().split()
            if parts[0] in seg_ids:
                seg_ids[parts[0]] += 1
            else:
                seg_ids[parts[0]] = 1

            for w in parts[1:]:
                try:
                    vocab[w] += 1
                except KeyError:
                    vocab[w] = 1

    return vocab, seg_ids


def write_list_to_file(fname, lst):
    """ Write list or tuple of lists or set into file """

    with codecs.open(fname, 'w', 'utf-8') as fpw:
        if isinstance(lst, list):
            fpw.write("\n".join(lst) + "\n")
        elif isinstance(lst, tuple):
            for i, _ in enumerate(lst[0]):
                fpw.write(lst[0][i] + " " + lst[1][i] + "\n")


def load_file_to_list(fname, col=None, sep=' ', return_tuple=False):
    """ load file, line by line into list. if col given, load only the column.
    col index starts from zero """

    lst = []

    if return_tuple:
        lst = ([], [])

    with codecs.open(fname, 'r', 'utf-8') as fpr:
        for line in fpr:
            line = line.strip()

            if return_tuple or col:
                parts = line.split(sep)
                lst[0].append(parts[0])
                lst[1].append(parts[1])

                if col:
                    lst.append(parts[col])
            else:
                lst.append(line.strip())

    return lst




def main():
    """ main method """

    args = parse_arguments()

    os.makedirs(args.out_dir, exist_ok=True)
    out_dir = os.path.realpath(args.out_dir)

    out_sfx = f"{out_dir}/{args.lang}_wlen_{args.wlen}_sl_{args.sl}"
    # out_sfx += f"_nwords_{args.nwords}"

    kw_filter = KeywordFilter(args.lang, args.sl, args.wlen)

    # Load lexicon and create word2int mapping
    kw_filter.load_lexicon(args.lex_fname)

    # 1. Filter words based on word length
    words_f1_file = f"{out_dir}/{args.lang}_wlen_{args.wlen}.txt"
    if os.path.exists(words_f1_file):
        print("Loading existing file:", words_f1_file)
        words_f1 = set(load_file_to_list(words_f1_file))
    else:
        words_f1 = kw_filter.filter_kw_wlen(args.plot,
                                            words_f1_file.replace("txt", "png"))
        write_list_to_file(words_f1_file, list(words_f1))

    # 2. Filter words based on similarity
    words_f2_file = f"{out_dir}/{args.lang}_sl_{args.sl}.txt"
    if os.path.exists(words_f2_file):
        print("Loading existing file:", words_f2_file)
        word_pairs_f2 = load_file_to_list(words_f2_file, return_tuple=True)
    else:
        word_pairs_f2 = kw_filter.filter_similar_words(args.plot, out_dir,
                                                       words_f2_file.replace(
                                                           "txt", "png"))
        write_list_to_file(words_f2_file, word_pairs_f2)

    inter_pairs_f1_f2 = kw_filter.apply_12(words_f1, word_pairs_f2)

    f1_f2_file = f"{out_dir}/{args.lang}_word_pairs_wlen_{args.wlen}.txt"
    write_list_to_file(f1_f2_file, inter_pairs_f1_f2)
    print("File saved:", f1_f2_file)

    vocab, seg_ids = get_vocab_and_seg_ids(args.train)
    if args.test:
        vocab, seg_ids = get_vocab_and_seg_ids(args.test, vocab=vocab,
                                               seg_ids=seg_ids)
    if args.plot:
        plt.figure(3)
        plt.xticks(np.arange(1, 11))
        plt.xlabel('Word frequency bin')
        plt.ylabel('Frequency')
        plt.hist(list(vocab.values()), bins=np.arange(1, 11))
        plt.grid(alpha=0.3, linestyle='--')
        plt.savefig(f"{out_dir}/{args.lang}_word_freq.png", dpi=300)
        plt.show()

    # 3. Filter words based on frequency
    # words_f3 = kw_filter.filter_based_on_freq(args.train, args.test, args.plot)
    words = []
    freqs = np.zeros(shape=(len(vocab)), dtype=np.uint32)
    i = 0
    for word, freq in vocab.items():
        words.append(word)
        freqs[i] = freq
        i += 1

    # ipdb.set_trace()
    sim_1, sim_2 = inter_pairs_f1_f2
    for f in range(1, args.wfreq+1):
        ixs = np.where(freqs == f)[0]

        words_f = set([words[i] for i in ixs])

        out_1 = f"{out_sfx}_wfreq_{f}.txt"
        write_list_to_file(out_1, list(set(sim_1) & words_f))
        print("File saved:", out_1)

        x_pairs = ([], [])
        out_2 = f"{out_sfx}_wfreq_{f}_pairs.txt"
        for i, w in enumerate(sim_1):
            if w in words_f:
                x_pairs[0].append(w)
                x_pairs[1].append(sim_2[i])
        write_list_to_file(out_2, x_pairs)
        print("File saved:", out_2)


def parse_arguments():
    """ Parse command line arguments """

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("lang", choices=['tel', 'tam', 'guj'],
                        help='language')
    parser.add_argument("lex_fname", help="path to lexicon.txt")
    parser.add_argument("out_dir", help="output directory to save keywords, \
                        plots, etc")

    parser.add_argument('-wlen', type=int, default=3, required=True,
                        help='filter words based on length i.e., \
                            number of phones')
    parser.add_argument('-sl', type=int, default=1, required=True,
                        help='filter words based on similarity \
                            computed with Levenshtein distance')
    parser.add_argument('-wfreq', type=int, default=4, required=True,
                        help='filter based on word frequency from training \
                            and/or test segments file')
    parser.add_argument('-nwords', type=int, default=300, required=True,
                        help='approximate number of final keywords \
                        after applying one or more filters')
    parser.add_argument('-train', required=True, help='path to training \
        text file in Kaldi format (utt_id text)')
    parser.add_argument('-test', required=True, help='path to test text \
        file  in Kaldi format (utt_id text)')

    parser.add_argument('--plot', action='store_true', help='plot histograms \
        wherever applicable')

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    main()