import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from auto_utils import get_word_count, get_kw_count, load_keywords, get_wset, get_wlen, get_wfreq, CAP, CUP, write_kw_to_file


PATHS = {
    "telugu": [
        "../check_rttm/telugu/keywords_v2.txt",
        "Telugu/train/train.txt",
        "Telugu/test/test.txt",
    ]
}



def main():

    keywords = load_keywords(args.keyword_file)

    print("# keywords", len(keywords))

    train_kw_count = get_word_count(args.train_text)
    dev_kw_count = get_word_count(args.dev_text)
    test_kw_count = get_word_count(args.test_text)

    train_wset = get_wset(train_kw_count)
    dev_wset = get_wset(dev_kw_count)
    test_wset = get_wset(test_kw_count)

    train_count = get_wfreq(train_kw_count)
    dev_count = get_wfreq(dev_kw_count)
    test_count = get_wfreq(test_kw_count)

    tdt_set = (test_wset & train_wset) & dev_wset
    print(f"C = (train {CAP} dev {CAP} test):", len(tdt_set))

    tt_set = (train_wset & test_wset) - tdt_set
    print(f"T = (train {CAP} test) - C  :", len(tt_set))

    dt_set = (dev_wset & test_wset) - tdt_set
    print(f"D = (dev   {CAP} test) - C  :", len(dt_set))

    t_set = test_wset - (tdt_set | tt_set | dt_set)
    print(f"test - (C {CUP} T {CUP} D)      :", len(t_set))

    write_kw_to_file(t_set, "tamil_info/test_only.txt")
    write_kw_to_file(test_wset, "tamil_info/test_all.txt")
    write_kw_to_file((train_wset | dev_wset) - t_set, "tamil_info/train_and_dev_only.txt")


    not_in_train = {}
    not_in_train_count = []
    for kw in keywords:
        if kw not in train_kw_count:
            not_in_train[kw] = test_kw_count[kw]
            not_in_train_count.append(test_kw_count[kw])

    print("Not in train:", len(not_in_train))

    sys.exit()
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
