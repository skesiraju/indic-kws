#!/bin/bash

if [ $# -lt 3 ]; then
    echo "usage: $0 <lang> <wfreq> <wlen> [sfx: _uniq]"
    exit;
fi

set -e

export LC_ALL="en_US.utf-8"

lang=$1
wfreq=$2
wlen=$3
sfx=${4:-""}

python3 local/merge_two_kw_files.py ${lang}_keywords/sel/wf_1_wlen_${wlen}_sub_1 \
       ${lang}_keywords/sel/wfreq/wfreq_${wfreq}.txt \
       ${lang}_keywords/sel/wfreq_${wfreq}a


kws_utils/kws_one_simple.sh ${lang} ${lang}_keywords/rttm \
                            data/test${sfx}/ecf.xml \
                            ${lang}_keywords/sel/wfreq_${wfreq}a \
                            data/lang data/test${sfx} \
                            exp_mfcc/tri6_nnet_smbr/decode_test${sfx}/ \
                            10 1

python3 local/merge_two_kw_files.py ${lang}_keywords/sel/wf_${wfreq}_wlen_${wlen}_sub_1 \
       ${lang}_keywords/sel/wlen//wlen_${wlen}.txt \
       ${lang}_keywords/sel/wlen_${wlen}a


kws_utils/kws_one_simple.sh ${lang} ${lang}_keywords/rttm \
                            data/test${sfx}/ecf.xml \
                            ${lang}_keywords/sel/wlen_${wlen}a \
                            data/lang data/test${sfx} \
                            exp_mfcc/tri6_nnet_smbr/decode_test${sfx}/ \
                            10 1
