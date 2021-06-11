
import sys
import numpy as np

if len(sys.argv) != 2:
    print(sys.argv[0], 'utt2dur file')
    sys.exit()


utt2dur = np.loadtxt(sys.argv[1], usecols=[1])
print(
    "{:6d} utts, total dur {:4.2f} hr, avg dur {:4.2f} sec".format(
        utt2dur.shape[0], (utt2dur.sum() / 3600.),  utt2dur.mean())
)
