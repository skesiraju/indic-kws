#!/usr/bin/env python3

import os
import sys
import argparse
import random
import numpy as np
# import matplotlib.pyplot as plt
np.set_printoptions(threshold=4)


# PATHS = ["data/train/text", "data/dev/text", "data/test/text"]

CAP = u"\u2229"
CUP = u"\u222A"

def load_lexicon(lex_file):

    print("Loading lexicon from file:", lex_file)
    print("  Return dict will have: {word_1: [ph_1, ph_2, ph_3 ...], ...}")
    lex = {}
    with open(lex_file, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            line = line.strip()
            parts = line.split("\t")
            lex[parts[0].strip()] = parts[1].split()
    return lex


def load_keywords(keywords_file):

    keywords = set()
    with open(keywords_file, 'r', encoding='utf-8') as fpr:
        for line in fpr:
            line = line.strip()
            parts = line.split()
            if len(parts) == 1:
                keywords.add(parts[0])
            elif len(parts) == 2:
                keywords.add(parts[-1])
            else:
                print("keywords file should have either 1 or 2 columns. Found:",
                      line)
                sys.exit()
    return keywords


def get_kw_and_word_count(trans_file, keywords):

    word_count = {}
    kw_count = {}
    with open(trans_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()
            for tok in tokens:
                if tok in keywords:
                    try:
                        kw_count[tok] += 1
                    except KeyError:
                        kw_count[tok] = 1
                try:
                    word_count[tok] += 1
                except KeyError:
                    word_count[tok] = 1

    print("Found", len(kw_count), "keywords in", trans_file,
          "({:3.1f}%)".format(len(kw_count) * 100 / len(keywords)))
    print("  Total number of unique words:", len(word_count))

    return kw_count, word_count


def get_word_count(trans_file):

    word_count = {}
    # kw_count = {}
    with open(trans_file, "r", encoding="utf-8") as fpr:
        for line in fpr:
            tokens = line.strip().split()
            for tok in tokens[1:]:
                try:
                    word_count[tok] += 1
                except KeyError:
                    word_count[tok] = 1

    print("  Total number of unique words:", len(word_count))

    return word_count



def arrange_into_freq_bins(counts, max_bin):

    bin_sizes, bins = np.histogram(counts, bins=np.arange(1, max_bin))
    print('bin sizes:', bin_sizes.tolist(), 'sum:', sum(bin_sizes))
    # print('bins     :', bins)



# def do_selection(word2count, lex, word_set, max_lim, ratios):

#     # t_counts = []
#     # t_wlens = []

#     bin_dict = {}  # nested dict {wfreq_1: {wlen_3: [...], wlen_4: [...], ...}, wfreq_2: {...}, ...}

#     for w in word_set:

#         freq_w = word2count[w]
#         len_w = len(lex[w])

#         sub_dict = {}
#         if freq_w in bin_dict:
#             sub_dict = bin_dict[freq_w]

#         try:
#             sub_dict[len_w].append(w)
#         except KeyError:
#             sub_dict[len_w] = [w]

#         bin_dict[freq_w] = sub_dict

#     print('------------------------------------')
#     print('bin_dict:', len(bin_dict))

#     selection = []

#     wlen_seq = np.arange(15, 4, -1).astype(int)

#     for i, wf in enumerate(range(1, 11, 1)):
#         try:
#             sub_selection = []
#             sub_dict = bin_dict[wf]
#             max_words_for_wf = int(max_lim * ratios[i])
#             print('max words for wf:', max_words_for_wf, end=" ")
#             avg_per_wlen = max(2, (max_words_for_wf // len(sub_dict)))
#             print('avg no. of words per wlen:', avg_per_wlen)
#             for wlen, word_list in sub_dict.items():
#                 if 3 <= wlen <= 15:
#                     random.shuffle(word_list)
#                     print('wf', wf, 'wlen', wlen, len(word_list))
#                     if len(word_list) > avg_per_wlen:
#                         sub_selection.extend(word_list[:avg_per_wlen])
#                     else:
#                         sub_selection.extend(word_list)

#             # sub_selection = sub_dict[wlen_seq[i]]
#             # random.shuffle(sub_selection)
#             selection.extend(sub_selection)
#             print(wf, ratios[i], 'cum sum:', len(selection))

#         except KeyError:
#             continue
#             # print("wf:", wf, "not in bin dict")
#             # sys.exit()


#     return selection


def do_selection(word2count, lex, word_set, max_lim, ratios, wfreq=0):

    # t_counts = []
    # t_wlens = []

    bin_dict = {}  # nested dict {wfreq_1: {wlen_3: [...], wlen_4: [...], ...}, wfreq_2: {...}, ...}

    for w in word_set:

        freq_w = word2count[w]
        len_w = len(lex[w])

        sub_dict = {}
        if freq_w in bin_dict:
            sub_dict = bin_dict[freq_w]

        try:
            sub_dict[len_w].append(w)
        except KeyError:
            sub_dict[len_w] = [w]

        bin_dict[freq_w] = sub_dict

    print('------------------------------------')
    print('bin_dict:', len(bin_dict))

    selection = []

    # wlen_seq = np.arange(15, 3, -1).astype(int)

    wlen_range = [3, 15]

    for i, wf in enumerate(range(1, 20, 1)):
        if wfreq != 0 and wf != wfreq:
            continue
        try:
            sub_selection = []
            sub_dict = bin_dict[wf]
            max_words_for_wf = int(max_lim * ratios[i])
            print('max words for wf:', wf, max_words_for_wf, end=" ")
            avg_per_wlen = max(
                max_words_for_wf // len(sub_dict),
                (max_words_for_wf // (wlen_range[1] - wlen_range[0]))
            )
            print('avg no. of words per wlen:', avg_per_wlen)
            for wlen, word_list in sub_dict.items():
                if wlen_range[0] <= wlen <= wlen_range[1]:
                    random.shuffle(word_list)
                    print('wf', wf, 'wlen', wlen, len(word_list))
                    if len(word_list) > avg_per_wlen:
                        sub_selection.extend(word_list[:avg_per_wlen])
                    else:
                        sub_selection.extend(word_list)

            # sub_selection = sub_dict[wlen_seq[i]]
            # random.shuffle(sub_selection)
            selection.extend(sub_selection)
            print(wf, ratios[i], 'cum sum:', len(selection))

        except KeyError:
            continue
            # print("wf:", wf, "not in bin dict")
            # sys.exit()


    return selection



get_wset = lambda w_count: set([k for k in w_count])

get_wlen = lambda w_count, lex: [len(lex[k]) for k in w_count]

get_wfreq = lambda w_count: [v for k, v in w_count.items()]


def write_kw_to_file(keywords, fname):

    with open(fname, 'w', encoding='utf-8') as fpw:
         for i, k in enumerate(keywords):
             fpw.write(str(i+1) + " " + k + "\n")

    print(len(keywords), "keywords saved to", fname)


def main():
    """ main method """

    # keywords = set()
    # with open(args.keywords_file, "r", encoding="utf-8") as fpr:
    #     for line in fpr:
    #         if len(line.strip().split()) == 2:
    #             keywords.add(line.strip().split()[-1])
    #         else:
    #             keywords.add(line.strip())

    # print("Loaded", len(keywords), "keywords from", args.keywords_file)

    data_dir = args.data_dir

    lex = load_lexicon(os.path.join(data_dir, "local/dict/lexicon.txt"))
    print("* Lexicon:", len(lex))

    train_w_count = get_word_count(os.path.join(data_dir, "train/text"))
    dev_w_count = get_word_count(os.path.join(data_dir, "dev/text"))
    test_w_count = get_word_count(os.path.join(data_dir, "test/text"))

    train_wset = get_wset(train_w_count)
    dev_wset = get_wset(dev_w_count)
    test_wset = get_wset(test_w_count)

    train_count = get_wfreq(train_w_count)
    dev_count = get_wfreq(dev_w_count)
    test_count = get_wfreq(test_w_count)

    print("== word occurrence ==")
    arrange_into_freq_bins(train_count, args.max_bin)
    arrange_into_freq_bins(dev_count, args.max_bin)
    arrange_into_freq_bins(test_count, args.max_bin)

    print("== word length ==")
    train_w_lens = get_wlen(train_w_count, lex)
    arrange_into_freq_bins(train_w_lens, args.max_bin)

    dev_w_lens = get_wlen(dev_w_count, lex)
    arrange_into_freq_bins(dev_w_lens, args.max_bin)

    test_w_lens = get_wlen(test_w_count, lex)
    arrange_into_freq_bins(test_w_lens, args.max_bin)


    tdt_set = (test_wset & train_wset) & dev_wset
    print(f"C = (train {CAP} dev {CAP} test):", len(tdt_set))

    tt_set = (train_wset & test_wset) - tdt_set
    print(f"T = (train {CAP} test) - C  :", len(tt_set))

    dt_set = (dev_wset & test_wset) - tdt_set
    print(f"D = (dev   {CAP} test) - C  :", len(dt_set))

    t_set = test_wset - (tdt_set | tt_set | dt_set)
    print(f"test - (C {CUP} T {CUP} D)      :", len(t_set))

    # tdt_counts = [test_w_count[w] for w in tdt_set]
    # arrange_into_freq_bins(tdt_counts, args.max_bin)

    # if args.wfreq == 0:

    #     max_lim = int(args.num_kw * args.test_ratio)
    #     ratios = [.13, .12, .12, .12, .12, .12, .09, .07, .06, .05]
    #     sel_tdt = do_selection(test_w_count, lex, tdt_set, max_lim, ratios)

    #     max_lim = int(args.num_kw * args.test_ratio)
    #     sel_tt = do_selection(test_w_count, lex, tt_set, max_lim, ratios)

    #     max_lim = int(args.num_kw * args.test_ratio)
    #     sel_dt = do_selection(test_w_count, lex, dt_set, max_lim, ratios)

    #     max_lim = int(args.num_kw * args.test_ratio)
    #     sel_t = do_selection(test_w_count, lex, t_set, max_lim, ratios)

    #     print(len(sel_tdt), len(sel_tt), len(sel_dt), len(sel_t))
    #     all_kw = sel_tdt + sel_tt + sel_dt + sel_t

    #     write_kw_to_file(sel_tdt, args.out_file + "_tdt")
    #     write_kw_to_file(sel_tt, args.out_file + "_tt")
    #     write_kw_to_file(sel_dt, args.out_file + "_dt")
    #     write_kw_to_file(sel_t, args.out_file + "_t")


    # else:
    #     # Select keywords corresponding to this wfreq only

    # args.test_ratio = 1

    max_lim = int(args.num_kw * args.test_ratio)
    ii = np.sort(np.random.randint(1, 1000, size=(args.max_wfreq)))[::-1]
    ratios = ii / ii.sum()
    print('ratios:', ratios.tolist())

    sel_tdt = do_selection(test_w_count, lex, tdt_set, max_lim, ratios, args.wfreq)

    max_lim = int(args.num_kw * args.test_ratio)
    sel_tt = do_selection(test_w_count, lex, tt_set, max_lim, ratios, args.wfreq)

    max_lim = int(args.num_kw * args.test_ratio)
    sel_dt = do_selection(test_w_count, lex, dt_set, max_lim, ratios, args.wfreq)

    max_lim = int(args.num_kw * args.test_ratio)
    sel_t = do_selection(test_w_count, lex, t_set, max_lim, ratios, args.wfreq)

    print(len(sel_tdt), len(sel_tt), len(sel_dt), len(sel_t))
    all_kw = sel_tdt + sel_tt + sel_dt + sel_t

    write_kw_to_file(sel_tdt, args.out_file + "_tdt")
    write_kw_to_file(sel_tt, args.out_file + "_tt")
    write_kw_to_file(sel_dt, args.out_file + "_dt")
    write_kw_to_file(sel_t, args.out_file + "_t")

    write_kw_to_file(all_kw, args.out_file)




if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # parser.add_argument("keywords_file", help="path to keywords file")
    parser.add_argument("data_dir", help="path to data dir")
    parser.add_argument("out_file", help="path to save keywords")
    parser.add_argument('-max_wfreq', type=int, default=20)
    parser.add_argument('-max_bin', type=int, default=10)
    parser.add_argument("-num_kw", type=int, default=5000, help="desired number of keywords")
    parser.add_argument("-test_ratio", type=float, default=0.3,
                        help="ratio of total keywords to test-only keywords")
    parser.add_argument("-wfreq", default=0, type=int)
    args = parser.parse_args()

    main()
