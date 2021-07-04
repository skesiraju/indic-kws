* Each directory contains data splits, `keywords` and `rttm` (ground truth for KWS as required by NIST F4DE)
* `train`, `dev`, `test` splits will have just the `utterance IDs`, `utt2spk` mapping.

* `hin`, `mar` and `ori` contains additional splits `dev_trim` and `test_trim` which are actually subsets of `dev` and `test` respectively. 
The trimmed versions are made for KWS experiments so as to have many words in low occurrence bins. Otherwise all the unique utts are present, 
and some utts even repeat few times.
