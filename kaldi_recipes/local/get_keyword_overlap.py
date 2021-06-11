import argparse
import numpy as np
import matplotlib.pyplot as plt
from auto_utils import (
    get_kw_count,
    get_word_count,
    load_keywords,
    get_wset,
    get_wlen,
    get_wfreq,
    CAP,
    CUP,
    arrange_into_freq_bins,
)

PRE = "/home/santosh/tools/kaldi/egs/indic/"
PATHS = {
    "tel": [
        "tel_keywords/OLD/sel_iter_22/iter_22_588.txt",
        "data/train/text",
        "data/test/text",
    ],
    "tam": ["tam_keywords/OLD/572_keywords.txt", "data/train/text", "data/test/text"],
    "guj": ["guj/596_keywords_Guj.txt", "data/train/text", "data/test/text"],
}


def main():

    keywords = load_keywords(args.keyword_file)

    print("# keywords", len(keywords))

    train_kw_count = get_kw_count(args.train_text, keywords)
    dev_kw_count = get_kw_count(args.dev_text, keywords)
    test_kw_count = get_kw_count(args.test_text, keywords)

    train_wset = get_wset(train_kw_count)
    dev_wset = get_wset(dev_kw_count)
    test_wset = get_wset(test_kw_count)

    train_count = get_wfreq(train_kw_count)
    dev_count = get_wfreq(dev_kw_count)
    test_count = get_wfreq(test_kw_count)

    test_w_count = get_word_count(args.train_text)
    arrange_into_freq_bins(get_wfreq(test_w_count), 25)

    tdt_set = (test_wset & train_wset) & dev_wset
    print(f"C = (train {CAP} dev {CAP} test):", len(tdt_set))

    tt_set = (train_wset & test_wset) - tdt_set
    print(f"T = (train {CAP} test) - C  :", len(tt_set))

    dt_set = (dev_wset & test_wset) - tdt_set
    print(f"D = (dev   {CAP} test) - C  :", len(dt_set))

    t_set = test_wset - (tdt_set | tt_set | dt_set)
    print(f"test - (C {CUP} T {CUP} D)      :", len(t_set))

    not_in_train = {}
    not_in_train_count = []
    for kw in keywords:
        if kw not in train_kw_count:
            not_in_train[kw] = test_kw_count[kw]
            not_in_train_count.append(test_kw_count[kw])

    print("Not in train:", len(not_in_train))

    density = False

    plt.rc("text", usetex=True)
    plt.style.use("thesis")
    plt.figure()

    plt.hist(
        train_count,
        bins=np.unique(train_count),
        color="C0",
        density=density,
        label="Training",
        alpha=0.5,
    )
    plt.hist(
        test_count,
        bins=np.unique(test_count),
        color="C1",
        density=density,
        label="Test",
        alpha=0.5,
    )
    plt.hist(
        not_in_train_count,
        bins=np.unique(not_in_train_count),
        color="C2",
        density=density,
        label="Not in training",
        alpha=0.5,
    )
    plt.xlabel("Keyword occurrence bin")
    plt.ylabel("Number of occurrences")
    plt.grid()
    plt.legend(loc="best")
    plt.show()

    print(np.histogram(test_count, bins=np.unique(test_count))[1].tolist())
    print(not_in_train_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword_file")
    parser.add_argument("-train_text", default="data/train/text")
    parser.add_argument("-dev_text", default="data/dev/text")
    parser.add_argument("-test_text", default="data/test/text")

    args = parser.parse_args()

    main()
