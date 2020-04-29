## Installing required packages
-----------------------------

### Option 1: Using Anaconda installation

    conda install matplotlib numpy -y
    conda install -c conda-forge python-levenshtein -y

### Option 2: Using default system-wide `python3`

    sudo apt install python3-pip
    python3 -m pip install numpy matplotlib
    python3 -m pip install python-Levenshtein

## Usage
--------

* Display help:

    `python3 prep_keywords.py --help`

* Example usage:

    `python3 prep_keywords.py tel telugu/lexicon.txt telugu_keywords/ -wlen 3 -sl 1 -nwords 300 -train telugu/train_text -test telugu/test_text`